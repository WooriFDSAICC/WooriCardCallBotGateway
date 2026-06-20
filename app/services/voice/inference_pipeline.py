from __future__ import annotations

import logging

from app.config import settings
from app.constants.fds import FdsConstants
from app.models.stream_result import StreamAnalysisResult
from app.services.voice.analysis_result_builder import AnalysisResultBuilder
from app.services.voice.audio_preprocessor import AudioPreprocessor
from app.services.voice.triton_client import TritonInferenceClient

logger = logging.getLogger(__name__)


class InferencePipeline:
    """오디오 청크 → 전처리 → Triton 추론 → FDS 결과 생성 파이프라인."""

    def __init__(
        self,
        preprocessor: AudioPreprocessor,
        triton_client: TritonInferenceClient,
        result_builder: AnalysisResultBuilder | None = None,
    ) -> None:
        self._preprocessor = preprocessor
        self._triton = triton_client
        self._result_builder = result_builder or AnalysisResultBuilder()

    async def process_chunk(
        self,
        session_id: str,
        chunk_index: int,
        raw_pcm_bytes: bytes,
    ) -> StreamAnalysisResult | None:
        preprocessed = await self._preprocessor.preprocess(
            raw_pcm_bytes, session_id, chunk_index
        )

        stt_result = await self._triton.infer_stt(session_id, chunk_index, preprocessed)
        asd_result = await self._triton.infer_asd(session_id, chunk_index, preprocessed)

        if chunk_index > settings.escalation_chunk_threshold:
            logger.warning(
                "[Pipeline] Escalation triggered session=%s chunk=%d",
                session_id,
                chunk_index,
            )
            return self._result_builder.build_escalation(
                session_id, chunk_index, stt_result, asd_result
            )

        if chunk_index % settings.partial_result_interval != 0:
            return None

        if not stt_result.text:
            return None

        return self._result_builder.build_partial(
            session_id, chunk_index, stt_result, asd_result
        )

    @staticmethod
    def is_escalation_result(result: StreamAnalysisResult) -> bool:
        return result.event == FdsConstants.EVENT_AGENT_ESCALATION

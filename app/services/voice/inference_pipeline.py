from __future__ import annotations

import logging

from app.config import settings
from app.constants.call_direction import CallDirection
from app.constants.fds import FdsConstants
from app.constants.integration_contract import EVENT_AGENT_ESCALATION
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

    def build_outbound_opening(
        self,
        session_id: str,
        campaign_id: str | None,
    ) -> StreamAnalysisResult:
        return self._result_builder.build_outbound_opening(session_id, campaign_id)

    async def process_chunk(
        self,
        session_id: str,
        chunk_index: int,
        raw_pcm_bytes: bytes,
        call_direction: CallDirection = CallDirection.INBOUND,
        campaign_id: str | None = None,
    ) -> StreamAnalysisResult | None:
        preprocessed = await self._preprocessor.preprocess(
            raw_pcm_bytes, session_id, chunk_index
        )

        stt_result = await self._triton.infer_stt(session_id, chunk_index, preprocessed)
        asd_result = await self._triton.infer_asd(session_id, chunk_index, preprocessed)

        escalation_threshold = self._resolve_escalation_threshold(call_direction, campaign_id)
        if chunk_index > escalation_threshold:
            logger.warning(
                "[Pipeline] Escalation triggered session=%s direction=%s chunk=%d",
                session_id,
                call_direction.value,
                chunk_index,
            )
            return self._result_builder.build_escalation(
                session_id,
                chunk_index,
                stt_result,
                asd_result,
                call_direction=call_direction,
                campaign_id=campaign_id,
            )

        if chunk_index % settings.partial_result_interval != 0:
            return None

        if not stt_result.text:
            return None

        return self._result_builder.build_partial(
            session_id,
            chunk_index,
            stt_result,
            asd_result,
            call_direction=call_direction,
            campaign_id=campaign_id,
        )

    @staticmethod
    def _resolve_escalation_threshold(
        call_direction: CallDirection,
        campaign_id: str | None,
    ) -> int:
        if call_direction == CallDirection.OUTBOUND and campaign_id:
            return max(settings.escalation_chunk_threshold - 5, 5)
        return settings.escalation_chunk_threshold

    @staticmethod
    def is_escalation_result(result: StreamAnalysisResult) -> bool:
        return (
            result.event == EVENT_AGENT_ESCALATION
            or result.fds_flag == FdsConstants.FLAG_CRITICAL
        )

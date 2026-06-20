from app.constants.fds import FdsConstants
from app.services.voice.inference_models import AsdInferenceOutput, SttInferenceOutput
from app.models.stream_result import StreamAnalysisResult


class AnalysisResultBuilder:
    """FDS 분석 결과 JSON 빌더."""

    @staticmethod
    def build_escalation(
        session_id: str,
        chunk_index: int,
        stt_result: SttInferenceOutput,
        asd_result: AsdInferenceOutput,
    ) -> StreamAnalysisResult:
        text = FdsConstants.ESCALATION_MOCK_TEXT
        return StreamAnalysisResult(
            status=FdsConstants.STATUS_PROCESSING,
            fds_flag=FdsConstants.FLAG_CRITICAL,
            event=FdsConstants.EVENT_AGENT_ESCALATION,
            text=text,
            stt_text=text,
            fds_score=max(asd_result.spoof_score, FdsConstants.ESCALATION_MIN_FDS_SCORE),
            reason=FdsConstants.ESCALATION_MOCK_REASON,
            metadata={
                FdsConstants.METADATA_SESSION_ID: session_id,
                FdsConstants.METADATA_CHUNK_INDEX: chunk_index,
                FdsConstants.METADATA_ASD_SPOOF_SCORE: asd_result.spoof_score,
                FdsConstants.METADATA_STT_CONFIDENCE: stt_result.confidence,
                FdsConstants.METADATA_TRIGGER: FdsConstants.TRIGGER_CHUNK_THRESHOLD,
            },
        )

    @staticmethod
    def build_partial(
        session_id: str,
        chunk_index: int,
        stt_result: SttInferenceOutput,
        asd_result: AsdInferenceOutput,
    ) -> StreamAnalysisResult:
        fds_flag = (
            FdsConstants.FLAG_WARNING
            if asd_result.is_suspicious
            else FdsConstants.FLAG_NORMAL
        )
        return StreamAnalysisResult(
            status=FdsConstants.STATUS_PROCESSING,
            fds_flag=fds_flag,
            event=FdsConstants.EVENT_STT_PARTIAL,
            text=stt_result.text,
            stt_text=stt_result.text,
            fds_score=asd_result.spoof_score,
            metadata={
                FdsConstants.METADATA_SESSION_ID: session_id,
                FdsConstants.METADATA_CHUNK_INDEX: chunk_index,
                FdsConstants.METADATA_STT_CONFIDENCE: stt_result.confidence,
                FdsConstants.METADATA_ASD_SPOOF_SCORE: asd_result.spoof_score,
                FdsConstants.METADATA_IS_PARTIAL: stt_result.is_partial,
            },
        )

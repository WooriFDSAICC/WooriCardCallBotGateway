from app.constants.call_direction import CallDirection
from app.constants.fds import FdsConstants
from app.constants.integration_contract import EVENT_STT_PARTIAL
from app.config import settings
from app.services.voice.inference_models import AsdInferenceOutput, SttInferenceOutput
from app.models.stream_result import StreamAnalysisResult


class AnalysisResultBuilder:
    """FDS 분석 결과 JSON 빌더."""

    @staticmethod
    def _base_metadata(
        session_id: str,
        chunk_index: int | None,
        call_direction: CallDirection,
        campaign_id: str | None,
        **extra: object,
    ) -> dict:
        metadata: dict = {
            FdsConstants.METADATA_SESSION_ID: session_id,
            FdsConstants.METADATA_CALL_DIRECTION: call_direction.value,
            **extra,
        }
        if chunk_index is not None:
            metadata[FdsConstants.METADATA_CHUNK_INDEX] = chunk_index
        if campaign_id:
            metadata[FdsConstants.METADATA_CAMPAIGN_ID] = campaign_id
        return metadata

    @staticmethod
    def build_outbound_opening(
        session_id: str,
        campaign_id: str | None,
    ) -> StreamAnalysisResult:
        text = settings.outbound_opening_ment_text
        return StreamAnalysisResult(
            status=FdsConstants.STATUS_PROCESSING,
            fds_flag=FdsConstants.FLAG_NORMAL,
            event=EVENT_STT_PARTIAL,
            text=text,
            stt_text=text,
            fds_score=0.0,
            metadata=AnalysisResultBuilder._base_metadata(
                session_id,
                None,
                CallDirection.OUTBOUND,
                campaign_id,
                **{FdsConstants.METADATA_SPEAKER: FdsConstants.SPEAKER_BOT},
            ),
        )

    @staticmethod
    def build_escalation(
        session_id: str,
        chunk_index: int,
        stt_result: SttInferenceOutput,
        asd_result: AsdInferenceOutput,
        call_direction: CallDirection = CallDirection.INBOUND,
        campaign_id: str | None = None,
    ) -> StreamAnalysisResult:
        text = FdsConstants.ESCALATION_MOCK_TEXT
        reason = FdsConstants.ESCALATION_MOCK_REASON
        if call_direction == CallDirection.OUTBOUND:
            reason = "Outbound campaign FDS critical — agent handoff"

        return StreamAnalysisResult(
            status=FdsConstants.STATUS_PROCESSING,
            fds_flag=FdsConstants.FLAG_CRITICAL,
            event=FdsConstants.EVENT_AGENT_ESCALATION,
            text=text,
            stt_text=text,
            fds_score=max(asd_result.spoof_score, FdsConstants.ESCALATION_MIN_FDS_SCORE),
            reason=reason,
            metadata=AnalysisResultBuilder._base_metadata(
                session_id,
                chunk_index,
                call_direction,
                campaign_id,
                **{
                    FdsConstants.METADATA_ASD_SPOOF_SCORE: asd_result.spoof_score,
                    FdsConstants.METADATA_STT_CONFIDENCE: stt_result.confidence,
                    FdsConstants.METADATA_TRIGGER: FdsConstants.TRIGGER_CHUNK_THRESHOLD,
                    FdsConstants.METADATA_SPEAKER: FdsConstants.SPEAKER_CUSTOMER,
                },
            ),
        )

    @staticmethod
    def build_partial(
        session_id: str,
        chunk_index: int,
        stt_result: SttInferenceOutput,
        asd_result: AsdInferenceOutput,
        call_direction: CallDirection = CallDirection.INBOUND,
        campaign_id: str | None = None,
    ) -> StreamAnalysisResult:
        fds_flag = (
            FdsConstants.FLAG_WARNING
            if asd_result.is_suspicious
            else FdsConstants.FLAG_NORMAL
        )
        if call_direction == CallDirection.OUTBOUND and asd_result.spoof_score >= FdsConstants.OUTBOUND_WARNING_SCORE:
            fds_flag = FdsConstants.FLAG_WARNING

        return StreamAnalysisResult(
            status=FdsConstants.STATUS_PROCESSING,
            fds_flag=fds_flag,
            event=EVENT_STT_PARTIAL,
            text=stt_result.text,
            stt_text=stt_result.text,
            fds_score=asd_result.spoof_score,
            metadata=AnalysisResultBuilder._base_metadata(
                session_id,
                chunk_index,
                call_direction,
                campaign_id,
                **{
                    FdsConstants.METADATA_STT_CONFIDENCE: stt_result.confidence,
                    FdsConstants.METADATA_ASD_SPOOF_SCORE: asd_result.spoof_score,
                    FdsConstants.METADATA_IS_PARTIAL: stt_result.is_partial,
                    FdsConstants.METADATA_SPEAKER: FdsConstants.SPEAKER_CUSTOMER,
                },
            ),
        )

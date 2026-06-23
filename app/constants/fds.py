from dataclasses import dataclass

from app.constants.integration_contract import EVENT_AGENT_ESCALATION, EVENT_STT_PARTIAL


@dataclass(frozen=True)
class FdsConstants:
    """FDS 분석 결과 및 이벤트 상수."""

    STATUS_PROCESSING: str = "PROCESSING"

    FLAG_NORMAL: str = "NORMAL"
    FLAG_WARNING: str = "WARNING"
    FLAG_CRITICAL: str = "CRITICAL"

    EVENT_STT_PARTIAL: str = EVENT_STT_PARTIAL
    EVENT_AGENT_ESCALATION: str = EVENT_AGENT_ESCALATION

    ESCALATION_MOCK_TEXT: str = "검찰청 금융범죄수사과입니다."
    ESCALATION_MOCK_REASON: str = "Voice phishing pattern detected (mock scenario)"
    ESCALATION_MIN_FDS_SCORE: float = 0.97
    OUTBOUND_WARNING_SCORE: float = 0.55

    METADATA_SESSION_ID: str = "session_id"
    METADATA_CHUNK_INDEX: str = "chunk_index"
    METADATA_CALL_DIRECTION: str = "call_direction"
    METADATA_CAMPAIGN_ID: str = "campaign_id"
    METADATA_ASD_SPOOF_SCORE: str = "asd_spoof_score"
    METADATA_STT_CONFIDENCE: str = "stt_confidence"
    METADATA_IS_PARTIAL: str = "is_partial"
    METADATA_TRIGGER: str = "trigger"
    METADATA_SPEAKER: str = "speaker"
    SPEAKER_BOT: str = "bot"
    SPEAKER_CUSTOMER: str = "customer"
    TRIGGER_CHUNK_THRESHOLD: str = "chunk_threshold_exceeded"

    ASD_SUSPICIOUS_THRESHOLD: float = 0.7

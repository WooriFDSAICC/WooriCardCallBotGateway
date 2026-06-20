from dataclasses import dataclass


@dataclass(frozen=True)
class FdsConstants:
    """FDS 분석 결과 및 이벤트 상수."""

    STATUS_PROCESSING: str = "PROCESSING"

    FLAG_NORMAL: str = "NORMAL"
    FLAG_WARNING: str = "WARNING"
    FLAG_CRITICAL: str = "CRITICAL"

    EVENT_STT_PARTIAL: str = "STT_PARTIAL"
    EVENT_AGENT_ESCALATION: str = "AGENT_ESCALATION"

    ESCALATION_MOCK_TEXT: str = "검찰청 금융범죄수사과입니다."
    ESCALATION_MOCK_REASON: str = "Voice phishing pattern detected (mock scenario)"
    ESCALATION_MIN_FDS_SCORE: float = 0.97

    METADATA_SESSION_ID: str = "session_id"
    METADATA_CHUNK_INDEX: str = "chunk_index"
    METADATA_ASD_SPOOF_SCORE: str = "asd_spoof_score"
    METADATA_STT_CONFIDENCE: str = "stt_confidence"
    METADATA_IS_PARTIAL: str = "is_partial"
    METADATA_TRIGGER: str = "trigger"
    TRIGGER_CHUNK_THRESHOLD: str = "chunk_threshold_exceeded"

    ASD_SUSPICIOUS_THRESHOLD: float = 0.7

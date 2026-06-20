"""AI팀·백엔드 연동 계약 (스키마 v1.0). Relay IntegrationContracts.java 와 동기화."""
from dataclasses import dataclass


@dataclass(frozen=True)
class IntegrationContract:
    SCHEMA_VERSION: str = "1.0"

    TRITON_MODEL_STT: str = "stt_streaming"
    TRITON_MODEL_ASD: str = "asd_voiceprint"
    TRITON_MODEL_FDS: str = "fds_lgbm"

    TRITON_INFER_PATH: str = "/v2/models/{model}/infer"
    TRITON_HEALTH_READY_PATH: str = "/v2/health/ready"

    # STT infer inputs
    INPUT_CHUNK_INDEX: str = "CHUNK_INDEX"
    INPUT_ESCALATION_THRESHOLD: str = "ESCALATION_THRESHOLD"
    INPUT_SESSION_ID: str = "SESSION_ID"

    # STT infer outputs
    OUTPUT_TEXT: str = "TEXT"
    OUTPUT_CONFIDENCE: str = "CONFIDENCE"
    OUTPUT_IS_PARTIAL: str = "IS_PARTIAL"

    # ASD infer outputs
    OUTPUT_SPOOF_SCORE: str = "SPOOF_SCORE"
    OUTPUT_IS_SUSPICIOUS: str = "IS_SUSPICIOUS"

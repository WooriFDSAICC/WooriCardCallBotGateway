from dataclasses import dataclass


@dataclass(frozen=True)
class TritonConstants:
    """Triton Inference Server 연동 상수."""

    DEFAULT_HTTP_URL: str = "http://localhost:8001"
    DEFAULT_STT_MODEL: str = "stt_streaming"
    DEFAULT_ASD_MODEL: str = "asd_voiceprint"
    DEFAULT_FDS_MODEL: str = "fds_lgbm"

    INFER_PATH_TEMPLATE: str = "/v2/models/{model}/infer"

    HTTP_TIMEOUT_SECONDS: float = 5.0
    HTTP_CONNECT_TIMEOUT_SECONDS: float = 2.0

    DEFAULT_ESCALATION_CHUNK_THRESHOLD: int = 20
    DEFAULT_PARTIAL_RESULT_INTERVAL: int = 5

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.constants.audio import AudioConstants
from app.constants.triton import TritonConstants


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "WooriCallbotGateway"
    host: str = "0.0.0.0"
    port: int = 8000

    triton_http_url: str = TritonConstants.DEFAULT_HTTP_URL
    triton_stt_model: str = TritonConstants.DEFAULT_STT_MODEL
    triton_asd_model: str = TritonConstants.DEFAULT_ASD_MODEL
    escalation_chunk_threshold: int = TritonConstants.DEFAULT_ESCALATION_CHUNK_THRESHOLD
    partial_result_interval: int = TritonConstants.DEFAULT_PARTIAL_RESULT_INTERVAL
    max_chunk_bytes: int = AudioConstants.DEFAULT_MAX_CHUNK_BYTES

    metrics_enabled: bool = True

    triton_startup_check: bool = True

    redis_enabled: bool = True
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0

    outbound_opening_ment_enabled: bool = True
    outbound_opening_ment_text: str = "안녕하세요, 우리카드입니다. 고객님께 안내드릴 내용이 있습니다."

settings = Settings()

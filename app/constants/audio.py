from dataclasses import dataclass


@dataclass(frozen=True)
class AudioConstants:
    """PCM 오디오 스트림 포맷 상수."""

    SAMPLE_RATE: int = 16_000
    SAMPLE_WIDTH_BYTES: int = 2
    CHANNELS: int = 1
    NORMALIZE_MIN: float = -1.0
    NORMALIZE_MAX: float = 1.0
    DEFAULT_MAX_CHUNK_BYTES: int = 65_536

from __future__ import annotations

import logging

import numpy as np

from app.config import settings
from app.constants.audio import AudioConstants

logger = logging.getLogger(__name__)


class AudioPreprocessor:
    """실시간 PCM 청크 전처리기."""

    async def preprocess(self, raw_bytes: bytes, session_id: str, chunk_index: int) -> bytes:
        if not raw_bytes:
            raise ValueError("Empty audio chunk received")

        if len(raw_bytes) > settings.max_chunk_bytes:
            raise ValueError(
                f"Chunk size {len(raw_bytes)} exceeds limit {settings.max_chunk_bytes}"
            )

        if len(raw_bytes) % AudioConstants.SAMPLE_WIDTH_BYTES != 0:
            raw_bytes = raw_bytes[
                : len(raw_bytes)
                - (len(raw_bytes) % AudioConstants.SAMPLE_WIDTH_BYTES)
            ]

        samples = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32)
        if samples.size == 0:
            raise ValueError("No valid PCM samples in chunk")

        peak = np.max(np.abs(samples))
        if peak > 0:
            samples = samples / peak

        normalized = np.clip(
            samples,
            AudioConstants.NORMALIZE_MIN,
            AudioConstants.NORMALIZE_MAX,
        )
        preprocessed = normalized.astype(np.float32).tobytes()

        logger.debug(
            "[Preprocessor] session=%s chunk=%d raw=%dB preprocessed=%dB samples=%d",
            session_id,
            chunk_index,
            len(raw_bytes),
            len(preprocessed),
            samples.size,
        )
        return preprocessed

    @staticmethod
    def estimate_duration_ms(pcm16_bytes: bytes) -> float:
        sample_count = len(pcm16_bytes) // AudioConstants.SAMPLE_WIDTH_BYTES
        return (sample_count / AudioConstants.SAMPLE_RATE) * 1000.0

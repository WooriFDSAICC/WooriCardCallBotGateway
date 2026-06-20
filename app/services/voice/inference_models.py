from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SttInferenceOutput:
    text: str
    confidence: float
    is_partial: bool


@dataclass
class AsdInferenceOutput:
    spoof_score: float
    is_suspicious: bool

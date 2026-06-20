from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, model_validator

from app.constants.fds import FdsConstants


class StreamAnalysisResult(BaseModel):
    """Spring Boot Relay로 전송하는 실시간 분석 JSON."""

    status: str = Field(default=FdsConstants.STATUS_PROCESSING)
    fds_flag: str = Field(default=FdsConstants.FLAG_NORMAL)
    event: str = Field(default=FdsConstants.EVENT_STT_PARTIAL)
    text: str = Field(default="")
    stt_text: str = Field(default="")
    fds_score: float = Field(default=0.0, ge=0.0, le=1.0)
    reason: Optional[str] = Field(default=None)
    metadata: Optional[Dict[str, Any]] = Field(default=None)

    @model_validator(mode="after")
    def sync_text_fields(self) -> "StreamAnalysisResult":
        if self.text and not self.stt_text:
            self.stt_text = self.text
        elif self.stt_text and not self.text:
            self.text = self.stt_text
        return self

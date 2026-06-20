from __future__ import annotations

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class StreamSessionState:
    """
    WebSocket 세션별 런타임 상태.
    청크 카운터만 유지하고 오디오 바이너리는 누적하지 않아 메모리 누수를 방지한다.
    """

    session_id: str
    chunk_count: int = 0
    total_bytes_received: int = 0
    is_active: bool = True
    escalation_sent: bool = False
    _cleanup_done: bool = field(default=False, repr=False)

    def increment(self, byte_length: int) -> int:
        self.chunk_count += 1
        self.total_bytes_received += byte_length
        return self.chunk_count

    def mark_escalation_sent(self) -> None:
        self.escalation_sent = True

    def cleanup(self) -> None:
        if self._cleanup_done:
            return
        self.is_active = False
        self._cleanup_done = True
        logger.info(
            "[SessionState] cleaned session=%s chunks=%d bytes=%d escalation=%s",
            self.session_id,
            self.chunk_count,
            self.total_bytes_received,
            self.escalation_sent,
        )


class SessionStateRegistry:
    """활성 WebSocket 세션 상태 레지스트리 (in-memory, asyncio-safe 단일 이벤트 루프)."""

    def __init__(self) -> None:
        self._sessions: dict[str, StreamSessionState] = {}

    def create(self, session_id: str) -> StreamSessionState:
        state = StreamSessionState(session_id=session_id)
        self._sessions[session_id] = state
        return state

    def get(self, session_id: str) -> StreamSessionState | None:
        return self._sessions.get(session_id)

    def remove(self, session_id: str) -> StreamSessionState | None:
        return self._sessions.pop(session_id, None)

    def active_count(self) -> int:
        return len(self._sessions)

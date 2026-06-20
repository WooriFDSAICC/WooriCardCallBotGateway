from dataclasses import dataclass


@dataclass(frozen=True)
class WebSocketConstants:
    """WebSocket 프로토콜 및 라우팅 상수."""

    STREAM_PATH: str = "/v1/stream/{session_id}"
    HEALTH_PATH: str = "/health"

    MSG_DISCONNECT: str = "websocket.disconnect"
    MSG_RECEIVE: str = "websocket.receive"

    CLOSE_NORMAL: int = 1000
    CLOSE_MESSAGE_TOO_BIG: int = 1009
    CLOSE_INTERNAL_ERROR: int = 1011

    CLOSE_REASON_SESSION_ENDED: str = "session ended"
    CLOSE_REASON_CHUNK_EXCEEDED: str = "Chunk size exceeded"
    CLOSE_REASON_INTERNAL_ERROR: str = "Internal server error"
    CLOSE_REASON_MAX_LENGTH: int = 120

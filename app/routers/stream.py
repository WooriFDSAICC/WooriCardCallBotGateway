from __future__ import annotations

from fastapi import APIRouter, WebSocket

from app.constants.websocket import WebSocketConstants
from app.services.voice.stream_session_service import StreamSessionService

router = APIRouter(tags=["voice-stream"])
stream_session_service = StreamSessionService()


@router.websocket(WebSocketConstants.STREAM_PATH)
async def voice_stream(websocket: WebSocket, session_id: str) -> None:
    """Spring Boot Relay → 콜봇 모델 게이트웨이 실시간 오디오 스트림 엔드포인트."""
    await stream_session_service.handle_stream(websocket, session_id)

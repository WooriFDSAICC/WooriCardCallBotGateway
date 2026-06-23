from __future__ import annotations

from fastapi import APIRouter, WebSocket

from app.constants.call_direction import CallDirection
from app.constants.websocket import WebSocketConstants
from app.services.voice.stream_session_service import StreamSessionService

router = APIRouter(tags=["voice-stream"])
stream_session_service = StreamSessionService()


@router.websocket(WebSocketConstants.STREAM_INBOUND_PATH)
async def voice_stream_inbound(websocket: WebSocket, session_id: str) -> None:
    """Relay INBOUND — 고객 인입 상담/문의 시나리오."""
    await stream_session_service.handle_stream(websocket, session_id, CallDirection.INBOUND)


@router.websocket(WebSocketConstants.STREAM_OUTBOUND_PATH)
async def voice_stream_outbound(websocket: WebSocket, session_id: str) -> None:
    """Relay OUTBOUND — 캠페인 발신 시나리오."""
    await stream_session_service.handle_stream(websocket, session_id, CallDirection.OUTBOUND)


@router.websocket(WebSocketConstants.STREAM_PATH)
async def voice_stream_legacy(websocket: WebSocket, session_id: str) -> None:
    """레거시 경로 — INBOUND와 동일 처리."""
    await stream_session_service.handle_stream(websocket, session_id, CallDirection.INBOUND)

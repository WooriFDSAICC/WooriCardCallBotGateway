from __future__ import annotations

import logging

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect, WebSocketState

from app.config import settings
from app.constants.websocket import WebSocketConstants
from app.models.stream_result import StreamAnalysisResult
from app.services.voice.inference_pipeline import InferencePipeline
from app.session_registry import SessionStateRegistry, StreamSessionState

logger = logging.getLogger(__name__)


class StreamSessionService:
    """WebSocket 스트림 세션 처리 — 수신/검증/추론/피드백/정리 전담."""

    async def handle_stream(self, websocket: WebSocket, session_id: str) -> None:
        pipeline: InferencePipeline = websocket.app.state.inference_pipeline
        registry: SessionStateRegistry = websocket.app.state.session_registry

        await websocket.accept()
        session_state = registry.create(session_id)
        logger.info("[StreamSession] Connected session=%s", session_id)

        try:
            await self._receive_loop(websocket, session_id, session_state, pipeline)
        except WebSocketDisconnect as exc:
            logger.info(
                "[StreamSession] WebSocketDisconnect session=%s code=%s",
                session_id,
                exc.code,
            )
        except Exception:
            logger.exception("[StreamSession] Unexpected error session=%s", session_id)
            await self._close_with_error(websocket)
        finally:
            await self._cleanup(
                websocket,
                session_state,
                registry,
                WebSocketConstants.CLOSE_REASON_SESSION_ENDED,
            )

    async def _receive_loop(
        self,
        websocket: WebSocket,
        session_id: str,
        session_state: StreamSessionState,
        pipeline: InferencePipeline,
    ) -> None:
        while session_state.is_active:
            message = await websocket.receive()

            if message["type"] == WebSocketConstants.MSG_DISCONNECT:
                break

            if message["type"] != WebSocketConstants.MSG_RECEIVE:
                continue

            raw_bytes = message.get("bytes")
            if raw_bytes is None:
                if message.get("text"):
                    logger.debug("[StreamSession] Ignored text frame session=%s", session_id)
                continue

            if not raw_bytes:
                continue

            if len(raw_bytes) > settings.max_chunk_bytes:
                logger.warning(
                    "[StreamSession] Chunk too large session=%s size=%d",
                    session_id,
                    len(raw_bytes),
                )
                await websocket.close(
                    code=WebSocketConstants.CLOSE_MESSAGE_TOO_BIG,
                    reason=WebSocketConstants.CLOSE_REASON_CHUNK_EXCEEDED,
                )
                break

            chunk_index = session_state.increment(len(raw_bytes))
            result = await pipeline.process_chunk(session_id, chunk_index, raw_bytes)

            if result is None:
                continue

            if not await self._send_result(websocket, session_id, result):
                break

            if InferencePipeline.is_escalation_result(result):
                session_state.mark_escalation_sent()
                break

    async def _send_result(
        self,
        websocket: WebSocket,
        session_id: str,
        result: StreamAnalysisResult,
    ) -> bool:
        if websocket.client_state != WebSocketState.CONNECTED:
            return False
        await websocket.send_text(result.model_dump_json())
        logger.info(
            "[StreamSession] Sent result session=%s event=%s fds_flag=%s",
            session_id,
            result.event,
            result.fds_flag,
        )
        return True

    async def _close_with_error(self, websocket: WebSocket) -> None:
        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.close(
                    code=WebSocketConstants.CLOSE_INTERNAL_ERROR,
                    reason=WebSocketConstants.CLOSE_REASON_INTERNAL_ERROR,
                )
            except RuntimeError:
                pass

    async def _cleanup(
        self,
        websocket: WebSocket,
        session_state: StreamSessionState,
        registry: SessionStateRegistry,
        reason: str,
    ) -> None:
        session_id = session_state.session_id
        session_state.cleanup()
        registry.remove(session_id)

        if websocket.client_state == WebSocketState.CONNECTED:
            try:
                await websocket.close(
                    code=WebSocketConstants.CLOSE_NORMAL,
                    reason=reason[: WebSocketConstants.CLOSE_REASON_MAX_LENGTH],
                )
            except RuntimeError:
                pass

        logger.info("[StreamSession] Closed session=%s reason=%s", session_id, reason)

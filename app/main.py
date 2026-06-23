from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app import metrics as _metrics  # noqa: F401 — register Prometheus collectors
from app.constants.websocket import WebSocketConstants
from app.metrics import APPLICATION, triton_up
from app.routers import stream
from app.services.voice.analysis_result_builder import AnalysisResultBuilder
from app.services.voice.audio_preprocessor import AudioPreprocessor
from app.services.voice.inference_pipeline import InferencePipeline
from app.services.voice.triton_client import TritonInferenceClient
from app.session_registry import SessionStateRegistry
from app.utils.log_context import configure_logging
from app.utils.otel import instrument_fastapi
from app.utils.triton_health import check_triton_ready

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.triton_startup_check:
        ready = await check_triton_ready(settings.triton_http_url)
        triton_up.labels(application=APPLICATION).set(1 if ready else 0)
        if not ready:
            raise RuntimeError(f"Triton not ready: {settings.triton_http_url}")

    triton_client = TritonInferenceClient()
    await triton_client.startup()

    voice_pipeline = InferencePipeline(
        preprocessor=AudioPreprocessor(),
        triton_client=triton_client,
        result_builder=AnalysisResultBuilder(),
    )
    session_registry = SessionStateRegistry()

    app.state.triton_client = triton_client
    app.state.inference_pipeline = voice_pipeline
    app.state.session_registry = session_registry

    await stream.stream_session_service.startup()

    logger.info(
        "%s started port=%d triton_url=%s metrics=%s",
        settings.app_name,
        settings.port,
        settings.triton_http_url,
        settings.metrics_enabled,
    )

    yield

    await stream.stream_session_service.shutdown()
    await triton_client.shutdown()
    logger.info("%s shutdown complete", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="우리은행 콜봇 게이트웨이 — Voice STT/ASD 실시간 스트리밍 (Triton Model Worker 연동)",
    lifespan=lifespan,
)

instrument_fastapi(app)

if settings.metrics_enabled:
    Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

app.include_router(stream.router)


@app.get(WebSocketConstants.HEALTH_PATH)
async def health_check():
    ready = await check_triton_ready(settings.triton_http_url)
    triton_up.labels(application=APPLICATION).set(1 if ready else 0)
    return {
        "status": "UP" if ready else "DEGRADED",
        "service": settings.app_name,
        "capabilities": {
            "voice_stream": True,
            "voice_stream_inbound": True,
            "voice_stream_outbound": True,
        },
        "triton_http_url": settings.triton_http_url,
        "triton_ready": ready,
    }

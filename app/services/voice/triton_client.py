from __future__ import annotations

import logging
from typing import Any, Dict, List

import httpx

from app.config import settings
from app.constants.triton import TritonConstants
from app.services.voice.inference_models import AsdInferenceOutput, SttInferenceOutput

logger = logging.getLogger(__name__)


class TritonInferenceClient:
    """NVIDIA Triton Inference Server HTTP v2 클라이언트."""

    def __init__(self) -> None:
        self._http_client: httpx.AsyncClient | None = None

    async def startup(self) -> None:
        self._http_client = httpx.AsyncClient(
            base_url=settings.triton_http_url,
            timeout=httpx.Timeout(
                TritonConstants.HTTP_TIMEOUT_SECONDS,
                connect=TritonConstants.HTTP_CONNECT_TIMEOUT_SECONDS,
            ),
        )
        logger.info("[TritonClient] connected url=%s", settings.triton_http_url)

    async def shutdown(self) -> None:
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

    async def infer_stt(
        self,
        session_id: str,
        chunk_index: int,
        preprocessed_audio: bytes,
    ) -> SttInferenceOutput:
        data = await self._infer(
            settings.triton_stt_model,
            [
                {"name": "CHUNK_INDEX", "shape": [1], "datatype": "INT32", "data": [chunk_index]},
                {
                    "name": "ESCALATION_THRESHOLD",
                    "shape": [1],
                    "datatype": "INT32",
                    "data": [settings.escalation_chunk_threshold],
                },
                {"name": "SESSION_ID", "shape": [1], "datatype": "BYTES", "data": [session_id]},
            ],
        )
        outputs = _index_outputs(data.get("outputs") or [])
        return SttInferenceOutput(
            text=str(outputs.get("TEXT", "")),
            confidence=float(outputs.get("CONFIDENCE", 0.0)),
            is_partial=bool(outputs.get("IS_PARTIAL", True)),
        )

    async def infer_asd(
        self,
        session_id: str,
        chunk_index: int,
        preprocessed_audio: bytes,
    ) -> AsdInferenceOutput:
        data = await self._infer(
            settings.triton_asd_model,
            [
                {"name": "CHUNK_INDEX", "shape": [1], "datatype": "INT32", "data": [chunk_index]},
                {
                    "name": "ESCALATION_THRESHOLD",
                    "shape": [1],
                    "datatype": "INT32",
                    "data": [settings.escalation_chunk_threshold],
                },
                {"name": "SESSION_ID", "shape": [1], "datatype": "BYTES", "data": [session_id]},
            ],
        )
        outputs = _index_outputs(data.get("outputs") or [])
        return AsdInferenceOutput(
            spoof_score=float(outputs.get("SPOOF_SCORE", 0.0)),
            is_suspicious=bool(outputs.get("IS_SUSPICIOUS", False)),
        )

    async def _infer(self, model_name: str, inputs: List[Dict[str, Any]]) -> Dict[str, Any]:
        if self._http_client is None:
            raise RuntimeError("TritonInferenceClient not started")

        path = TritonConstants.INFER_PATH_TEMPLATE.format(model=model_name)
        response = await self._http_client.post(path, json={"inputs": inputs})
        response.raise_for_status()
        return response.json()


def _index_outputs(outputs: List[Dict[str, Any]]) -> Dict[str, Any]:
    indexed: Dict[str, Any] = {}
    for item in outputs:
        name = item.get("name")
        data = item.get("data")
        if name is None:
            continue
        if isinstance(data, list) and data:
            indexed[name] = data[0]
        else:
            indexed[name] = data
    return indexed

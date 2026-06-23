from __future__ import annotations

import logging
from typing import Optional

import redis.asyncio as aioredis

from app.config import settings
from app.constants.integration_contract import SESSION_REDIS_KEY_PREFIX

logger = logging.getLogger(__name__)

_REDIS_FIELD_CAMPAIGN_ID = "campaign_id"


class OutboundSessionLookup:
    """Relay가 적재한 아웃바운드 세션 Hash에서 campaign_id 조회."""

    def __init__(self) -> None:
        self._redis: Optional[aioredis.Redis] = None

    async def startup(self) -> None:
        if not settings.redis_enabled:
            return
        self._redis = aioredis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password or None,
            db=settings.redis_db,
            decode_responses=True,
        )

    async def shutdown(self) -> None:
        if self._redis:
            await self._redis.aclose()
            self._redis = None

    async def get_campaign_id(self, session_id: str) -> Optional[str]:
        if self._redis is None:
            return None
        key = f"{SESSION_REDIS_KEY_PREFIX}outbound:{session_id}"
        try:
            campaign_id = await self._redis.hget(key, _REDIS_FIELD_CAMPAIGN_ID)
            if campaign_id:
                logger.info("[OutboundLookup] campaign_id=%s session=%s", campaign_id, session_id)
            return campaign_id or None
        except Exception as exc:
            logger.warning("[OutboundLookup] Redis read failed session=%s: %s", session_id, exc)
            return None

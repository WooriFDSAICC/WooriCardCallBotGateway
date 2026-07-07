from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

APPLICATION = "WooriCallbotGateway"

callbot_active_sessions = Gauge(
    "callbot_active_sessions",
    "Active Callbot Gateway WebSocket sessions",
    ["direction", "application"],
)

callbot_stt_response_seconds = Histogram(
    "callbot_stt_response_seconds",
    "STT partial/escalation JSON generation latency",
    ["direction", "application"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

callbot_escalations_total = Counter(
    "callbot_escalations_total",
    "Escalation or CRITICAL fds_flag responses sent to Relay",
    ["direction", "application"],
)

triton_up = Gauge(
    "triton_up",
    "Triton inference server readiness (1=ready)",
    ["application"],
)

# ── TTS 발화 결정 발행(오디오 재생은 TTS Worker 담당) ──
callbot_tts_decisions_total = Counter(
    "callbot_tts_decisions_total",
    "Gateway 가 발행한 TTS 결정 이벤트",
    ["direction", "decision", "application"],   # decision: say|stop
)

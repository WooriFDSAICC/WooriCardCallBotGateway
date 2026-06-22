# WooriCardCallBotGateway ???�행 가?�드

FastAPI 기반 **Callbot Gateway**?�니?? Relay가 WebSocket?�로 PCM???�달?�면 Triton STT/ASD 추론 ??JSON(`FastApiStreamResult`)??반환?�니??

## ?�전 ?�구?�항

| ??�� | 버전 |
|------|------|
| Python | 3.12 |
| Triton (?�는 Mock) | HTTP `:8001` ??`WooriTritonMock` ?�는 ?�제 Triton |
| Redis (OUTBOUND ?? | ?�택 ??`campaign_id` 조회??|

---

## 1. Docker�??�행

### ?�체 ?�택 (Relay compose ?�함)

```powershell
cd MiddleWare\WooriCardCallBotRelayServer
docker compose up --build callbot-gateway
```

### Gateway ?��?지�?빌드·?�행

```powershell
cd MiddleWare\WooriCardCallBotGateway
docker build -t woori-callbot-gateway .
docker run --rm -p 8000:8000 `
  -e TRITON_HTTP_URL=http://host.docker.internal:8001 `
  -e REDIS_HOST=host.docker.internal `
  woori-callbot-gateway
```

Windows Docker Desktop?�서 `host.docker.internal`�??�스?�의 Triton/Redis???�근?�니??

---

## 2. 로컬 개발 ?�행

```powershell
cd MiddleWare\WooriCardCallBotGateway
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Triton Mock??먼�? ?�운 경우:

```powershell
cd ..\WooriTritonMock
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Gateway ?�행:

```powershell
cd MiddleWare\WooriCardCallBotGateway
$env:TRITON_HTTP_URL = "http://localhost:8001"
$env:TRITON_STARTUP_CHECK = "true"
uvicorn run:app --host 0.0.0.0 --port 8000 --reload
```

?�는:

```powershell
python -m uvicorn run:app --host 0.0.0.0 --port 8000 --reload
```

---

## 3. WebSocket ?�드?�인??

Relay(?�는 ?�스???�라?�언??가 ?�결?�는 URL:

| 경로 | ?�명 |
|------|------|
| `ws://localhost:8000/v1/stream/inbound/{sessionId}` | ?�바?�드 |
| `ws://localhost:8000/v1/stream/outbound/{sessionId}` | ?�웃바운??|
| `ws://localhost:8000/v1/stream/{sessionId}` | ?�거??(= INBOUND) |

**?�로?�콜**

- ?�신: Binary PCM (최�? 64KB/?�레??
- ?�신: Text JSON (`event`, `fds_flag`, `stt_text`, `fds_score` ??snake_case)

---

## 4. ?�경 변??

`.env` ?�일 ?�는 ???�경 변?�로 ?�정?�니??(`app/config.py`).

| 변??| 기본�?| ?�명 |
|------|--------|------|
| `TRITON_HTTP_URL` | http://localhost:8001 | Triton HTTP URL |
| `TRITON_STARTUP_CHECK` | true | 기동 ??Triton ready 검??|
| `ESCALATION_CHUNK_THRESHOLD` | (triton ?�수) | ?�스컬레?�션 �?�� ?�계�?|
| `PARTIAL_RESULT_INTERVAL` | (triton ?�수) | STT partial ?�송 간격(�?��) |
| `METRICS_ENABLED` | true | `/metrics` ?�출 |
| `REDIS_ENABLED` | true | OUTBOUND campaign Redis 조회 |
| `REDIS_HOST` | localhost | Redis ?�스??|
| `REDIS_PORT` | 6379 | Redis ?�트 |
| `OUTBOUND_OPENING_MENT_ENABLED` | true | ?�웃바운???�발??JSON |
| `OTEL_ENABLED` | false | OpenTelemetry (compose?�서??true) |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | http://localhost:4318/v1/traces | Jaeger OTLP |
| `OTEL_SERVICE_NAME` | WooriCallbotGateway | Trace ?�비?�명 |

---

## 5. ?�작 ?�인

```powershell
curl http://localhost:8000/health
curl http://localhost:8000/metrics
```

`triton_ready`가 `false`?�면 Triton Mock/?�버�?먼�? 기동?�세??

### ?�위 ?�스??

```powershell
pip install -r requirements.txt
pytest
```

---

## 6. Relay ?�동 ??참고

Relay `docker-compose` ?�경 변??

```
FASTAPI_WS_INBOUND_BASE_URL=ws://callbot-gateway:8000/v1/stream/inbound
FASTAPI_WS_OUTBOUND_BASE_URL=ws://callbot-gateway:8000/v1/stream/outbound
```

로컬?�서 Relay�??�로 ?�울 ?�는 `localhost:8000`?�로 ??URL??맞춥?�다.

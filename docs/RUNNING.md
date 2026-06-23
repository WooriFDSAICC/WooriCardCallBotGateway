# WooriCardCallBotGateway — 실행 가이드

FastAPI 기반 **Callbot Gateway**입니다. Relay가 WebSocket으로 PCM을 전달하면 Triton STT/ASD 추론 후 JSON(`FastApiStreamResult`)을 반환합니다.

## 사전 요구사항

| 항목 | 버전 |
|------|------|
| Python | 3.12 |
| Triton (또는 Mock) | HTTP `:8001` — `WooriTritonMock` 또는 실제 Triton |
| Redis (OUTBOUND 시) | 선택 — `campaign_id` 조회용 |

---

## 1. Docker로 실행

### 전체 스택 (Relay compose 포함)

```powershell
cd MiddleWare\WooriCardCallBotRelayServer
docker compose up --build callbot-gateway
```

### Gateway 이미지만 빌드·실행

```powershell
cd MiddleWare\WooriCardCallBotGateway
docker build -t woori-callbot-gateway .
docker run --rm -p 8000:8000 `
  -e TRITON_HTTP_URL=http://host.docker.internal:8001 `
  -e REDIS_HOST=host.docker.internal `
  woori-callbot-gateway
```

Windows Docker Desktop에서는 `host.docker.internal`로 호스트의 Triton/Redis에 접근합니다.

---

## 2. 로컬 개발 실행

```powershell
cd MiddleWare\WooriCardCallBotGateway
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Triton Mock을 먼저 띄운 경우:

```powershell
cd ..\WooriTritonMock
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Gateway 실행:

```powershell
cd MiddleWare\WooriCardCallBotGateway
$env:TRITON_HTTP_URL = "http://localhost:8001"
$env:TRITON_STARTUP_CHECK = "true"
uvicorn run:app --host 0.0.0.0 --port 8000 --reload
```

또는:

```powershell
python -m uvicorn run:app --host 0.0.0.0 --port 8000 --reload
```

---

## 3. WebSocket 엔드포인트

Relay(또는 테스트 클라이언트)가 연결하는 URL:

| 경로 | 설명 |
|------|------|
| `ws://localhost:8000/v1/stream/inbound/{sessionId}` | 인바운드 |
| `ws://localhost:8000/v1/stream/outbound/{sessionId}` | 아웃바운드 |
| `ws://localhost:8000/v1/stream/{sessionId}` | 레거시 (= INBOUND) |

**프로토콜**

- 송신: Binary PCM (최대 64KB/프레임)
- 수신: Text JSON (`event`, `fds_flag`, `stt_text`, `fds_score` 등 snake_case)

---

## 4. 환경 변수

`.env` 파일 또는 셸 환경 변수로 설정합니다 (`app/config.py`).

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `TRITON_HTTP_URL` | http://localhost:8001 | Triton HTTP URL |
| `TRITON_STARTUP_CHECK` | true | 기동 시 Triton ready 검사 |
| `ESCALATION_CHUNK_THRESHOLD` | (triton 상수) | 에스컬레이션 청크 임계값 |
| `PARTIAL_RESULT_INTERVAL` | (triton 상수) | STT partial 전송 간격(청크) |
| `METRICS_ENABLED` | true | `/metrics` 노출 |
| `REDIS_ENABLED` | true | OUTBOUND campaign Redis 조회 |
| `REDIS_HOST` | localhost | Redis 호스트 |
| `REDIS_PORT` | 6379 | Redis 포트 |
| `OUTBOUND_OPENING_MENT_ENABLED` | true | 아웃바운드 개시 멘트 JSON |
| `OTEL_ENABLED` | false | OpenTelemetry (compose에서는 true) |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | http://localhost:4318/v1/traces | Jaeger OTLP |
| `OTEL_SERVICE_NAME` | WooriCallbotGateway | Trace 서비스명 |

---

## 5. 동작 확인

```powershell
curl http://localhost:8000/health
curl http://localhost:8000/metrics
curl http://localhost:8000/docs   # Swagger UI
```

`triton_ready`가 `false`이면 Triton Mock/서버를 먼저 기동하세요.

### 단위 테스트

```powershell
pip install -r requirements.txt
pytest
```

---

## 6. Relay 연동 시 참고

Relay `docker-compose` 환경 변수:

```
FASTAPI_WS_INBOUND_BASE_URL=ws://callbot-gateway:8000/v1/stream/inbound
FASTAPI_WS_OUTBOUND_BASE_URL=ws://callbot-gateway:8000/v1/stream/outbound
```

로컬에서 Relay를 따로 띄울 때는 `localhost:8000`으로 위 URL을 맞춥니다.

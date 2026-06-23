# 기여 가이드 — 커밋 메시지

## 형식

```
<타입>: <한글 설명한다>. (#이슈번호)
```

### 타입

| 타입 | 용도 |
|------|------|
| `FEAT` | 기능 추가 |
| `FIX` | 버그 수정 |
| `CHORE` | 설정·빌드·인프라 |
| `TEST` | 테스트 |
| `DOCUMENT` | 문서 |

### 이슈 번호

- 커밋 메시지 **맨 끝**에 `(#N)` 형태로 GitHub 이슈 번호를 붙입니다.
- PR 본문에 `Closes #1` / `Ref #8` 등으로 추가 연결 가능합니다.

### 예시

```
FEAT: /v1/stream/inbound·outbound WebSocket 라우터를 추가한다. (#1)
TEST: Java IntegrationContracts와 Python 계약 동기화 테스트를 추가한다. (#8)
```

### 금지

- `Co-authored-by: Cursor <cursoragent@cursor.com>` 트레일러는 넣지 않습니다.

## Callbot 이슈 매핑 (v1.1)

| 이슈 | 범위 |
|------|------|
| #1 | Voice WebSocket Gateway |
| #2 | Triton HTTP v2 연동 |
| #3 | 에스컬레이션 임계값 |
| #8 | IntegrationContracts 동기화 테스트 |
| #9 | 아웃바운드 campaign_id Redis |
| #10 | Prometheus·OTEL |

https://github.com/WooriFDSAICC/WooriCardCallBotGateway/issues

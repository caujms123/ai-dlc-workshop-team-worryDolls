# Unit 3: Tech Stack Decisions - 주문 + SSE

> Unit 1에서 정의한 공통 Tech Stack을 그대로 사용합니다.
> Unit 3 특화 추가 사항만 기술합니다.

## Backend 추가 사항

| 영역 | 기술 | 선택 이유 |
|---|---|---|
| **SSE** | FastAPI StreamingResponse + asyncio | FastAPI 내장 SSE 지원, 비동기 이벤트 스트리밍 |
| **SSE 연결 관리** | In-memory dict (store_id → connections) | 단일 서버 환경, 간단한 구현 |
| **트랜잭션** | SQLAlchemy Session + async context manager | 주문 생성/이력 이동 원자성 보장 |

## Frontend 추가 사항

| 영역 | 기술 | 선택 이유 |
|---|---|---|
| **SSE Client** | 브라우저 내장 EventSource API | 표준 API, 자동 재연결 지원 |
| **실시간 UI 업데이트** | Vue reactivity + Pinia | SSE 이벤트 → Pinia store 업데이트 → UI 자동 반영 |
| **애니메이션** | CSS transition + Vue Transition | 신규 주문 하이라이트 효과 |

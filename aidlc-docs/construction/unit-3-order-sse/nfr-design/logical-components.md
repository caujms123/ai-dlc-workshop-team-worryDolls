# Unit 3: Logical Components - 주문 + SSE

---

## 1. SSE 아키텍처

```
+------------------+     +------------------+
| OrderService     |     | TableService     |
| (주문 생성/변경) |     | (이용 완료)      |
+------------------+     +------------------+
         |                        |
         v                        v
+----------------------------------------+
|           SSEManager (Singleton)       |
| admin_connections: {store_id: [Queue]} |
| customer_connections: {table_id: [Q]}  |
+----------------------------------------+
         |                        |
         v                        v
+------------------+     +------------------+
| Admin SSE Stream |     | Customer SSE     |
| (매장별)         |     | Stream (테이블별)|
+------------------+     +------------------+
```

---

## 2. 주문 처리 파이프라인

```
[주문 요청]
    |
    v
[입력 검증] (Pydantic)
    |
    v
[인증/인가] (AuthMiddleware)
    |
    v
[비즈니스 로직] (OrderService)
    |-- 세션 확인 (TableService)
    |-- 메뉴 검증 (MenuRepository)
    |-- 금액 계산
    |-- DB 저장 (트랜잭션)
    v
[이벤트 발행] (SSEManager)
    |
    v
[응답 반환]
```

---

## 3. SSE 이벤트 타입

| 이벤트 | 대상 | 페이로드 |
|---|---|---|
| `new_order` | 관리자 | 주문 요약 (번호, 테이블, 금액, 항목 미리보기) |
| `order_status_changed` | 관리자 + 고객 | 주문 ID, 새 상태 |
| `order_deleted` | 관리자 | 주문 ID, 테이블 ID |
| `table_completed` | 관리자 | 테이블 ID |

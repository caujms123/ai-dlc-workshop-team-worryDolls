# Unit 3: Code Generation Plan - 주문 + SSE (개발자 C)

---

## Unit Context

### 담당 스토리
| Story ID | Story 제목 | 페르소나 |
|---|---|---|
| US-MA-07 | 실시간 주문 대시보드 조회 | 매장 관리자 |
| US-MA-08 | 주문 상세 조회 | 매장 관리자 |
| US-MA-09 | 주문 상태 변경 | 매장 관리자 |
| US-MA-11 | 주문 삭제 (직권 수정) | 매장 관리자 |
| US-MA-12 | 테이블 이용 완료 처리 | 매장 관리자 |
| US-MA-13 | 과거 주문 내역 조회 | 매장 관리자 |
| US-CU-09 | 주문 확정 | 고객 |
| US-CU-10 | 현재 세션 주문 내역 조회 | 고객 |

### 의존성
- **Unit 1 제공**: AuthMiddleware (JWT 검증, RBAC), GlobalErrorHandler, database.py, config.py
- **Unit 2 제공**: MenuService.get_menu() (주문 시 메뉴 검증)
- **Unit 4 제공**: TableService.get_current_session() (주문 시 세션 확인)
- **Unit 3 → Unit 4 제공**: OrderService.create_order(), OrderService.move_to_history()

### 코드 위치
- **Backend**: `backend/app/` (models, routers, services, repositories, schemas)
- **Frontend Admin**: `frontend/admin/src/` (views, components, stores, services)
- **Frontend Customer**: `frontend/customer/src/` (views, components, stores, services)
- **Tests**: `backend/tests/`, `frontend/admin/tests/`, `frontend/customer/tests/`

---

## Code Generation Steps

### Step 1: Project Structure Setup (Backend - Unit 3 영역)
- [x] `backend/app/models/order.py` - Order, OrderItem, OrderHistory SQLAlchemy 모델
- [x] `backend/app/schemas/order.py` - Pydantic 요청/응답 스키마
- [x] `backend/app/schemas/sse.py` - SSE 이벤트 스키마
- [x] 디렉토리 구조 확인 및 `__init__.py` 파일 생성

**Story 매핑**: 전체 스토리 기반 인프라

---

### Step 2: Repository Layer - OrderRepository
- [x] `backend/app/repositories/order_repo.py`
  - `create(order, db)` → Order
  - `get_by_id(order_id, db)` → Order | None
  - `get_by_session(session_id, db)` → List[Order]
  - `get_by_store(store_id, db)` → List[Order]
  - `update_status(order_id, status, db)` → Order
  - `delete(order_id, db)` → None
  - `count_today_orders(store_id, today, db)` → int
  - `create_history(history, db)` → OrderHistory
  - `get_history_by_table(table_id, date_filter, db)` → List[OrderHistory]
  - `get_order_items(order_id, db)` → List[OrderItem]
  - `create_order_items(items, db)` → List[OrderItem]
  - `delete_order_items(order_id, db)` → None

**Story 매핑**: US-MA-07~09, US-MA-11~13, US-CU-09~10

---

### Step 3: Repository Layer Unit Testing
- [x] `backend/tests/test_order_repo.py`
  - Order CRUD 테스트
  - OrderItem CRUD 테스트
  - OrderHistory 생성/조회 테스트
  - count_today_orders 테스트
  - 세션별/매장별 조회 테스트

---

### Step 4: Repository Layer Summary
- [x] `aidlc-docs/construction/unit-3-order-sse/code/repository-layer-summary.md`

---

### Step 5: Business Logic - SSEService (SSE Manager)
- [x] `backend/app/services/sse_service.py`
  - SSEManager 클래스 (Singleton)
  - `subscribe_admin(store_id)` → asyncio.Queue
  - `unsubscribe_admin(store_id, queue)` → None
  - `subscribe_customer(table_id)` → asyncio.Queue
  - `unsubscribe_customer(table_id, queue)` → None
  - `publish_to_store(store_id, event)` → None
  - `publish_to_table(table_id, event)` → None
  - 연결 수 제한 (매장당 10개, 테이블당 3개)

**Story 매핑**: US-MA-07 (SSE 기반), US-CU-10 (SSE 기반)

---

### Step 6: Business Logic - OrderService
- [x] `backend/app/services/order_service.py`
  - `create_order(order_data, db)` → Order (US-CU-09)
    - 세션 확인/시작
    - 메뉴 유효성 검증 + 스냅샷
    - 주문 번호 생성 (ORD-YYYYMMDD-NNNN)
    - 금액 계산
    - DB 저장 (트랜잭션)
    - SSE 이벤트 발행 (new_order)
  - `get_table_orders(table_id, session_id, db)` → List[Order] (US-CU-10)
  - `get_store_orders(store_id, db)` → List[OrderSummary] (US-MA-07)
  - `update_order_status(order_id, new_status, store_id, db)` → Order (US-MA-09)
    - 상태 전이 검증 (PENDING→PREPARING→COMPLETED)
    - SSE 이벤트 발행 (order_status_changed)
  - `delete_order(order_id, store_id, db)` → None (US-MA-11)
    - SSE 이벤트 발행 (order_deleted)
  - `move_to_history(session_id, db)` → int (US-MA-12)
    - 주문 → OrderHistory 이동 (트랜잭션)
    - SSE 이벤트 발행 (table_completed)
  - `get_order_history(table_id, date_filter, db)` → List[OrderHistory] (US-MA-13)
  - `get_table_total(table_id, session_id, db)` → int

**Story 매핑**: US-MA-07~09, US-MA-11~13, US-CU-09~10

---

### Step 7: Business Logic Unit Testing
- [x] `backend/tests/test_order_service.py`
  - 주문 생성 성공/실패 테스트
  - 주문 번호 생성 테스트
  - 상태 전이 검증 테스트 (유효/무효)
  - 주문 삭제 테스트
  - 이력 이동 테스트
  - 매장 전체 주문 조회 테스트
- [x] `backend/tests/test_sse_service.py`
  - SSE 구독/해제 테스트
  - 이벤트 발행 테스트
  - 연결 수 제한 테스트

---

### Step 8: Business Logic Summary
- [x] `aidlc-docs/construction/unit-3-order-sse/code/business-logic-summary.md`

---

### Step 9: API Layer - Order Router
- [x] `backend/app/routers/order.py`
  - `POST /api/orders` - 주문 생성 (TABLE 역할) (US-CU-09)
  - `GET /api/tables/{table_id}/orders` - 테이블 현재 세션 주문 조회 (TABLE) (US-CU-10)
  - `GET /api/stores/{store_id}/orders` - 매장 전체 주문 조회 (STORE_ADMIN) (US-MA-07)
  - `PATCH /api/orders/{order_id}/status` - 주문 상태 변경 (STORE_ADMIN) (US-MA-09)
  - `DELETE /api/orders/{order_id}` - 주문 삭제 (STORE_ADMIN) (US-MA-11)
  - `POST /api/tables/{table_id}/complete` - 이용 완료 처리 (STORE_ADMIN) (US-MA-12)
  - `GET /api/tables/{table_id}/order-history` - 과거 주문 내역 (STORE_ADMIN) (US-MA-13)

---

### Step 10: API Layer - SSE Router
- [x] `backend/app/routers/sse.py`
  - `GET /api/sse/admin/stores/{store_id}/orders` - 관리자 SSE 스트림 (STORE_ADMIN) (US-MA-07)
  - `GET /api/sse/customer/tables/{table_id}/orders` - 고객 SSE 스트림 (TABLE) (US-CU-10)
  - StreamingResponse + keep-alive (30초)

---

### Step 11: API Layer Unit Testing
- [x] `backend/tests/test_order_router.py`
  - 각 엔드포인트 성공/실패 테스트
  - 인증/인가 테스트
  - 입력 검증 테스트
- [x] `backend/tests/test_sse_router.py`
  - SSE 연결 테스트
  - 인증 테스트

---

### Step 12: API Layer Summary
- [x] `aidlc-docs/construction/unit-3-order-sse/code/api-layer-summary.md`

---

### Step 13: Frontend - Admin OrderMonitorView
- [x] `frontend/admin/src/views/OrderView.vue` (US-MA-07, US-MA-08)
  - 테이블별 카드 그리드 레이아웃
  - SSE 연결 및 실시간 업데이트
  - 테이블 번호 필터링
  - 신규 주문 하이라이트 애니메이션

---

### Step 14: Frontend - Admin Order Components
- [x] `frontend/admin/src/components/order/TableOrderCard.vue` (US-MA-07)
  - 테이블 번호, 총 주문액, 최신 주문 미리보기
  - 신규 주문 펄스 애니메이션
- [x] `frontend/admin/src/components/order/OrderDetailPanel.vue` (US-MA-08, US-MA-09, US-MA-11, US-MA-12, US-MA-13)
  - 주문 목록 (시간순)
  - 상태 변경 버튼
  - 주문 삭제 버튼 (확인 팝업)
  - "이용 완료" 버튼 (확인 팝업)
  - "과거 내역" 버튼 + 날짜 필터

---

### Step 15: Frontend - Admin Order Store & Service
- [x] `frontend/admin/src/stores/orderStore.js` (Pinia)
  - tables, selectedTable, sseConnection 상태 관리
  - SSE 이벤트 핸들링
- [x] `frontend/admin/src/services/orderApi.js`
  - API 호출 함수들 (주문 조회, 상태 변경, 삭제, 이용 완료, 이력 조회)
  - SSE 연결 관리

---

### Step 16: Frontend - Customer OrderConfirmView
- [x] `frontend/customer/src/views/OrderView.vue` (US-CU-09)
  - 주문 내역 표시 (메뉴명, 수량, 단가, 소계)
  - 결제 방식 표시
  - 총 금액 표시
  - "주문 확정" 버튼
  - 성공: 주문 번호 표시 → 5초 후 메뉴 화면 리다이렉트
  - 실패: 에러 메시지

---

### Step 17: Frontend - Customer OrderHistoryView
- [x] `frontend/customer/src/views/OrderHistoryView.vue` (US-CU-10)
  - 주문 목록 (시간순)
  - 주문 번호, 시각, 메뉴/수량, 금액, 상태 배지
  - SSE 실시간 상태 업데이트
- [x] `frontend/customer/src/components/OrderConfirm.vue`
  - 주문 확정 컴포넌트 (재사용)

---

### Step 18: Frontend - Customer Order Store & Service
- [x] `frontend/customer/src/stores/orderStore.js` (Pinia)
  - orders, isLoading, sseConnection 상태 관리
- [x] `frontend/customer/src/services/orderApi.js`
  - API 호출 함수들 (주문 생성, 주문 조회)
  - SSE 연결 관리

---

### Step 19: Frontend Unit Testing
- [x] `frontend/admin/tests/components/order/TableOrderCard.spec.js`
- [x] `frontend/admin/tests/components/order/OrderDetailPanel.spec.js`
- [x] `frontend/admin/tests/views/OrderView.spec.js`
- [x] `frontend/admin/tests/stores/orderStore.spec.js`
- [x] `frontend/customer/tests/views/OrderView.spec.js`
- [x] `frontend/customer/tests/views/OrderHistoryView.spec.js`
- [x] `frontend/customer/tests/stores/orderStore.spec.js`

---

### Step 20: Frontend Components Summary
- [x] `aidlc-docs/construction/unit-3-order-sse/code/frontend-components-summary.md`

---

### Step 21: Database Migration Script
- [x] `backend/alembic/versions/003_create_order_tables.py`
  - Order 테이블 생성
  - OrderItem 테이블 생성
  - OrderHistory 테이블 생성
  - 인덱스 생성
  - FK 제약조건

**Story 매핑**: 전체 스토리 기반 인프라

---

### Step 22: Documentation
- [x] `aidlc-docs/construction/unit-3-order-sse/code/code-generation-summary.md`
  - 생성된 파일 목록
  - 스토리 커버리지
  - Security Extension 준수 사항

---

## Security Extension Compliance Plan

| 규칙 | 적용 방식 |
|---|---|
| SECURITY-03 | 구조화된 로깅 (OrderService, SSEService) |
| SECURITY-05 | Pydantic 입력 검증, 상태 전이 검증 |
| SECURITY-08 | JWT 인증, 역할 기반 접근 제어 (TABLE/STORE_ADMIN), 매장 스코프 검증 |
| SECURITY-09 | 프로덕션 에러 응답에 내부 정보 미노출 |
| SECURITY-11 | 보안 로직 분리 (AuthMiddleware), Rate Limiting |
| SECURITY-12 | JWT 토큰 검증 (매 요청), SSE 연결 인증 |
| SECURITY-13 | 트랜잭션 무결성 (주문 생성, 이력 이동) |
| SECURITY-15 | 전역 에러 핸들러, 트랜잭션 롤백, 리소스 정리 |

---

## 총 Step 수: 22
## 예상 파일 수: Backend 8개 + Tests 6개 + Frontend 12개 + Frontend Tests 7개 + Migration 1개 + Docs 4개 = 약 38개

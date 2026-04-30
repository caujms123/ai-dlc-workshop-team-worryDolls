# Unit 3: Frontend 컴포넌트 설계 - 주문 + 실시간 모니터링

---

## 1. Admin Frontend - 주문 모니터링

### OrderMonitorView.vue
**목적**: 실시간 주문 대시보드 (그리드 레이아웃)

**State**:
- `tables`: TableOrderSummary[] (테이블별 주문 요약)
- `selectedTable`: TableOrderSummary | null
- `filterTableNumber`: string
- `sseConnection`: EventSource | null

**사용자 상호작용**:
- 테이블별 카드 그리드 레이아웃
- 카드 클릭 → OrderDetail 패널 열기
- 테이블 번호 필터링
- 신규 주문 시 카드 하이라이트 애니메이션

**SSE 연동**:
- `GET /api/sse/admin/stores/{store_id}/orders` 구독
- `new_order` → 해당 테이블 카드 업데이트 + 하이라이트
- `order_status_changed` → 상태 반영
- `order_deleted` → 주문 제거 + 총액 재계산
- `table_completed` → 테이블 카드 리셋

### TableOrderCard.vue
**Props**: `tableData: TableOrderSummary`
**Emits**: `select`

**표시**: 테이블 번호, 총 주문액, 최신 주문 2~3개 미리보기, 주문 수
**스타일**: 신규 주문 시 배경색 변경 + 펄스 애니메이션 (3초)

### OrderDetailPanel.vue
**Props**: `tableId: number`, `storeId: number`
**Emits**: `close`, `statusChanged`, `orderDeleted`

**State**:
- `orders`: Order[]
- `showHistory`: boolean
- `historyOrders`: OrderHistory[]
- `dateFilter`: string

**사용자 상호작용**:
- 주문 목록 (시간순)
- 각 주문: 상태 변경 버튼 (PENDING→PREPARING→COMPLETED)
- 주문 삭제 버튼 (확인 팝업)
- "이용 완료" 버튼 (확인 팝업)
- "과거 내역" 버튼 → 과거 주문 목록
- 날짜 필터 (과거 내역)

**API 연동**:
- `GET /api/stores/{id}/orders` (테이블별)
- `PATCH /api/orders/{id}/status`
- `DELETE /api/orders/{id}`
- `POST /api/tables/{id}/complete`
- `GET /api/tables/{id}/order-history`

---

## 2. Customer Frontend - 주문

### OrderConfirmView.vue
**목적**: 주문 확정 화면

**Props** (route params): 장바구니 데이터, 결제 방식

**State**:
- `cartItems`: CartItem[]
- `paymentType`: 'DUTCH_PAY' | 'SINGLE_PAY'
- `totalAmount`: number
- `isSubmitting`: boolean
- `orderResult`: { success, orderNumber } | null

**사용자 상호작용**:
- 주문 내역 표시 (메뉴명, 수량, 단가, 소계)
- 결제 방식 표시
- 총 금액 표시
- "주문 확정" 버튼
- 성공: 주문 번호 표시 → 5초 후 메뉴 화면 자동 리다이렉트
- 실패: 에러 메시지 표시

**API 연동**:
- `POST /api/orders`

### OrderHistoryView.vue
**목적**: 현재 세션 주문 내역 조회

**State**:
- `orders`: Order[]
- `isLoading`: boolean
- `sseConnection`: EventSource | null

**사용자 상호작용**:
- 주문 목록 (시간순)
- 각 주문: 번호, 시각, 메뉴/수량, 금액, 상태 배지
- 상태 실시간 업데이트 (SSE)
- 무한 스크롤 또는 페이지네이션

**SSE 연동**:
- `GET /api/sse/customer/tables/{table_id}/orders` 구독
- `order_status_changed` → 해당 주문 상태 배지 업데이트

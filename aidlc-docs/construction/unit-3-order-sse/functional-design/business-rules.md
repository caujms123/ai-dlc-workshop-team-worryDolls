# Unit 3: 비즈니스 규칙 - 주문 + SSE

---

## 1. 주문 규칙

### BR-ORDER-01: 주문 생성
- 주문 항목이 1개 이상이어야 함
- 각 항목의 menu_id는 해당 매장의 유효한 메뉴여야 함
- 각 항목의 quantity는 1 이상
- total_amount = SUM(각 항목의 quantity * unit_price)
- 주문 시점의 메뉴명과 가격을 스냅샷으로 저장 (이후 메뉴 변경에 영향 없음)
- payment_type 필수 (DUTCH_PAY 또는 SINGLE_PAY)

### BR-ORDER-02: 주문 번호 생성
- 형식: `ORD-{YYYYMMDD}-{4자리 순번}`
- 예: `ORD-20260430-0001`
- 매일 순번 리셋
- 매장별 독립 순번

### BR-ORDER-03: 주문 상태 전이
```
PENDING → PREPARING → COMPLETED
```
- 역방향 전이 불가 (COMPLETED → PREPARING 불가)
- 상태 변경은 매장 관리자만 가능
- 상태 변경 시 SSE 이벤트 발행

### BR-ORDER-04: 주문 삭제
- 매장 관리자만 삭제 가능
- 삭제 시 해당 테이블의 총 주문액 재계산
- 삭제 시 SSE 이벤트 발행 (대시보드 갱신)
- 물리적 삭제 (soft delete 아님)

### BR-ORDER-05: 테이블 세션 주문 조회
- 현재 활성 세션의 주문만 반환
- 이용 완료된 세션의 주문은 제외
- 주문 시간 순 정렬 (최신 먼저)

---

## 2. 주문 이력 규칙

### BR-HISTORY-01: 이력 이동
- 테이블 이용 완료 시 해당 세션의 모든 주문을 OrderHistory로 복사
- 주문 항목은 JSON으로 직렬화하여 items_json에 저장
- completed_at에 이용 완료 시각 기록
- 원본 Order 및 OrderItem은 삭제

### BR-HISTORY-02: 이력 조회
- 매장 관리자만 조회 가능
- 테이블별, 날짜별 필터링 지원
- 시간 역순 정렬

---

## 3. SSE 규칙

### BR-SSE-01: 관리자 SSE 스트림
- 매장별 SSE 연결 (store_id 기반)
- 이벤트 유형: `new_order`, `order_status_changed`, `order_deleted`, `table_completed`
- 연결 유지: keep-alive 30초 간격
- 재연결: 클라이언트 자동 재연결 (EventSource 기본 동작)

### BR-SSE-02: 고객 SSE 스트림
- 테이블별 SSE 연결 (table_id 기반)
- 이벤트 유형: `order_status_changed`
- 현재 세션의 주문 상태 변경만 전달

### BR-SSE-03: SSE 이벤트 페이로드
```json
{
  "event_type": "new_order",
  "data": {
    "order_id": 1,
    "order_number": "ORD-20260430-0001",
    "table_id": 5,
    "table_number": 3,
    "total_amount": 25000,
    "items_preview": "김치찌개 x2, 된장찌개 x1",
    "status": "PENDING",
    "ordered_at": "2026-04-30T12:30:00"
  }
}
```

### BR-SSE-04: SSE 성능
- 이벤트 전달 지연: 2초 이내
- 동시 SSE 연결: 매장당 최대 10개, 테이블당 최대 3개

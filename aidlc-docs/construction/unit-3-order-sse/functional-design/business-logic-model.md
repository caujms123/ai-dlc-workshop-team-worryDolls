# Unit 3: 비즈니스 로직 모델 - 주문 + SSE

---

## 1. 주문 생성 플로우
```
입력: { table_id, payment_type, items: [{menu_id, quantity}] }
    |
    v
[테이블 인증 확인] (JWT: role=TABLE)
    |
    v
[항목 검증] -- 빈 목록 --> 422
    |
    v
[각 메뉴 유효성 확인] -- 메뉴 없음/비활성/다른 매장 --> 404
    |
    v
[현재 세션 확인]
    |-- 세션 없음 --> [새 세션 시작] (TableService)
    |-- 세션 있음 --> 계속
    v
[주문 번호 생성] (ORD-YYYYMMDD-NNNN)
    |
    v
[주문 항목 생성] (메뉴명, 단가 스냅샷)
    |
    v
[총 금액 계산] SUM(quantity * unit_price)
    |
    v
[DB 저장] (Order + OrderItems, 트랜잭션)
    |
    v
[SSE 이벤트 발행] → 관리자 (new_order)
    |
    v
출력: { order_id, order_number, total_amount, items, status }
```

## 2. 주문 상태 변경 플로우
```
입력: order_id, new_status
    |
    v
[주문 존재 확인] -- 없음 --> 404
    |
    v
[권한 확인] -- STORE_ADMIN, 해당 매장
    |
    v
[상태 전이 검증]
    |-- PENDING → PREPARING ✓
    |-- PREPARING → COMPLETED ✓
    |-- 기타 --> 422 (잘못된 상태 전이)
    v
[DB 업데이트]
    |
    v
[SSE 이벤트 발행]
    |-- 관리자 (order_status_changed)
    |-- 고객 (order_status_changed)
    v
출력: 수정된 Order 객체
```

## 3. 주문 삭제 플로우
```
입력: order_id
    |
    v
[주문 존재 확인] -- 없음 --> 404
    |
    v
[권한 확인] -- STORE_ADMIN
    |
    v
[OrderItem 삭제] (CASCADE)
    |
    v
[Order 삭제]
    |
    v
[SSE 이벤트 발행] → 관리자 (order_deleted)
    |
    v
출력: 204 No Content
```

## 4. 이용 완료 시 이력 이동 플로우
```
입력: session_id (TableService에서 호출)
    |
    v
[해당 세션의 모든 주문 조회]
    |
    v
[각 주문에 대해]
    |-- OrderItem을 JSON으로 직렬화
    |-- OrderHistory 레코드 생성
    |-- 원본 OrderItem 삭제
    |-- 원본 Order 삭제
    v
[트랜잭션 커밋]
    |
    v
출력: 이동된 주문 수
```

## 5. SSE 연결 관리 플로우
```
관리자 SSE 구독:
    입력: store_id (인증된 STORE_ADMIN)
    |
    v
    [SSE 연결 생성]
    |
    v
    [연결 풀에 등록] (store_id → connections[])
    |
    v
    [keep-alive 루프] (30초마다 ping)
    |
    v
    [연결 종료 시 풀에서 제거]

이벤트 발행:
    입력: store_id, event
    |
    v
    [해당 store_id의 모든 연결 조회]
    |
    v
    [각 연결에 이벤트 전송]
    |
    v
    [전송 실패한 연결 제거]
```

## 6. 매장 전체 주문 조회 (관리자 대시보드)
```
입력: store_id
    |
    v
[해당 매장의 활성 테이블 목록 조회]
    |
    v
[각 테이블별]
    |-- 현재 세션의 주문 목록
    |-- 총 주문액 계산
    |-- 최신 주문 n개 미리보기
    v
출력: [{ table_id, table_number, total_amount, orders: [...], latest_orders: [...] }]
```

# Unit 3: 도메인 엔티티 설계 - 주문 + SSE

---

## 1. Order (주문)

| 필드 | 타입 | 제약조건 | 설명 |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | 주문 고유 ID |
| order_number | VARCHAR(20) | UNIQUE, NOT NULL | 주문 번호 (표시용) |
| store_id | BIGINT | FK → Store.id, NOT NULL | 소속 매장 |
| table_id | BIGINT | FK → TableInfo.id, NOT NULL | 주문 테이블 |
| session_id | BIGINT | FK → TableSession.id, NOT NULL | 테이블 세션 |
| status | ENUM('PENDING','PREPARING','COMPLETED') | NOT NULL, DEFAULT 'PENDING' | 주문 상태 |
| payment_type | ENUM('DUTCH_PAY','SINGLE_PAY') | NOT NULL | 결제 방식 |
| total_amount | INT | NOT NULL | 총 주문 금액 |
| ordered_at | DATETIME | NOT NULL | 주문 시각 |
| updated_at | DATETIME | NOT NULL | 수정 시각 |

**인덱스**: `order_number` (UNIQUE), `(store_id, status)`, `(table_id, session_id)`

---

## 2. OrderItem (주문 항목)

| 필드 | 타입 | 제약조건 | 설명 |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | 항목 고유 ID |
| order_id | BIGINT | FK → Order.id, NOT NULL | 소속 주문 |
| menu_id | BIGINT | FK → Menu.id, NOT NULL | 메뉴 |
| menu_name | VARCHAR(100) | NOT NULL | 주문 시점 메뉴명 (스냅샷) |
| quantity | INT | NOT NULL, CHECK(quantity > 0) | 수량 |
| unit_price | INT | NOT NULL | 주문 시점 단가 (스냅샷) |
| subtotal | INT | NOT NULL | 소계 (quantity * unit_price) |

**관계**: OrderItem N:1 Order

---

## 3. OrderHistory (과거 주문 이력)

| 필드 | 타입 | 제약조건 | 설명 |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | 이력 고유 ID |
| original_order_id | BIGINT | NOT NULL | 원본 주문 ID |
| order_number | VARCHAR(20) | NOT NULL | 주문 번호 |
| store_id | BIGINT | FK → Store.id, NOT NULL | 소속 매장 |
| table_id | BIGINT | NOT NULL | 테이블 ID |
| session_id | BIGINT | NOT NULL | 세션 ID |
| status | VARCHAR(20) | NOT NULL | 최종 상태 |
| payment_type | VARCHAR(20) | NOT NULL | 결제 방식 |
| total_amount | INT | NOT NULL | 총 금액 |
| items_json | JSON | NOT NULL | 주문 항목 JSON 스냅샷 |
| ordered_at | DATETIME | NOT NULL | 원본 주문 시각 |
| completed_at | DATETIME | NOT NULL | 이용 완료 시각 |

**인덱스**: `(store_id, table_id, completed_at)`

---

## 4. ER 다이어그램

```
+------------------+       +------------------+
|     Order        |       |   OrderItem      |
+------------------+       +------------------+
| PK id            |<------| FK order_id      |
|    order_number  |       | PK id            |
| FK store_id      |       | FK menu_id       |
| FK table_id      |       |    menu_name     |
| FK session_id    |       |    quantity      |
|    status        |       |    unit_price    |
|    payment_type  |       |    subtotal      |
|    total_amount  |       +------------------+
|    ordered_at    |
+------------------+
        |
        v (이용 완료 시 이동)
+------------------+
|  OrderHistory    |
+------------------+
| PK id            |
|    order_number  |
|    items_json    |
|    completed_at  |
+------------------+
```

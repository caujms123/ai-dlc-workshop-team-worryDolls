# Unit 2: 도메인 엔티티 설계 - 메뉴 관리

---

## 1. Category (카테고리)

| 필드 | 타입 | 제약조건 | 설명 |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | 카테고리 고유 ID |
| store_id | BIGINT | FK → Store.id, NOT NULL | 소속 매장 |
| name | VARCHAR(50) | NOT NULL | 카테고리명 |
| display_order | INT | NOT NULL, DEFAULT 0 | 노출 순서 |
| created_at | DATETIME | NOT NULL | 생성 시각 |

**인덱스**: `(store_id, display_order)`
**관계**: Category N:1 Store

---

## 2. Menu (메뉴)

| 필드 | 타입 | 제약조건 | 설명 |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | 메뉴 고유 ID |
| store_id | BIGINT | FK → Store.id, NOT NULL | 소속 매장 |
| category_id | BIGINT | FK → Category.id, NOT NULL | 소속 카테고리 |
| name | VARCHAR(100) | NOT NULL | 메뉴명 |
| price | INT | NOT NULL, CHECK(price >= 0) | 가격 (원) |
| description | TEXT | NULLABLE | 메뉴 설명 |
| image_path | VARCHAR(500) | NULLABLE | 이미지 파일 경로 |
| display_order | INT | NOT NULL, DEFAULT 0 | 노출 순서 |
| is_available | BOOLEAN | DEFAULT TRUE | 판매 가능 여부 |
| created_at | DATETIME | NOT NULL | 생성 시각 |
| updated_at | DATETIME | NOT NULL | 수정 시각 |

**인덱스**: `(store_id, category_id, display_order)`, `(category_id)`
**관계**: Menu N:1 Category, Menu N:1 Store

---

## 3. ER 다이어그램

```
+------------------+       +------------------+
|     Store        |       |    Category      |
+------------------+       +------------------+
| PK id            |<------| FK store_id      |
+------------------+       | PK id            |
        |                  |    name          |
        |                  |    display_order |
        |                  +------------------+
        |                          |
        |                          v
        |                  +------------------+
        +----------------->|      Menu        |
                           +------------------+
                           | PK id            |
                           | FK store_id      |
                           | FK category_id   |
                           |    name          |
                           |    price         |
                           |    description   |
                           |    image_path    |
                           |    display_order |
                           |    is_available  |
                           +------------------+
```

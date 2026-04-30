# Unit 4: 도메인 엔티티 설계 - 고객 UI + 테이블 관리

---

## 1. TableInfo (테이블)

| 필드 | 타입 | 제약조건 | 설명 |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | 테이블 고유 ID |
| store_id | BIGINT | FK → Store.id, NOT NULL | 소속 매장 |
| table_number | INT | NOT NULL | 테이블 번호 |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt 해싱된 비밀번호 |
| is_active | BOOLEAN | DEFAULT TRUE | 활성 상태 |
| created_at | DATETIME | NOT NULL | 생성 시각 |
| updated_at | DATETIME | NOT NULL | 수정 시각 |

**인덱스**: `(store_id, table_number)` (UNIQUE)
**관계**: TableInfo N:1 Store

---

## 2. TableSession (테이블 세션)

| 필드 | 타입 | 제약조건 | 설명 |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | 세션 고유 ID |
| table_id | BIGINT | FK → TableInfo.id, NOT NULL | 테이블 |
| store_id | BIGINT | FK → Store.id, NOT NULL | 소속 매장 |
| started_at | DATETIME | NOT NULL | 세션 시작 시각 |
| ended_at | DATETIME | NULLABLE | 세션 종료 시각 (이용 완료 시) |
| is_active | BOOLEAN | DEFAULT TRUE | 활성 상태 |

**인덱스**: `(table_id, is_active)` - 현재 활성 세션 조회
**관계**: TableSession N:1 TableInfo

---

## 3. ER 다이어그램

```
+------------------+       +------------------+
|     Store        |       |   TableInfo      |
+------------------+       +------------------+
| PK id            |<------| FK store_id      |
+------------------+       | PK id            |
                           |    table_number  |
                           |    password_hash |
                           |    is_active     |
                           +------------------+
                                   |
                                   v
                           +------------------+
                           |  TableSession    |
                           +------------------+
                           | PK id            |
                           | FK table_id      |
                           | FK store_id      |
                           |    started_at    |
                           |    ended_at      |
                           |    is_active     |
                           +------------------+
```

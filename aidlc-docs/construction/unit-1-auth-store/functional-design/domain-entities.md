# Unit 1: 도메인 엔티티 설계 - 인증 + 매장 + 관리자 + 광고

---

## 1. Store (매장)

| 필드 | 타입 | 제약조건 | 설명 |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | 매장 고유 ID |
| store_code | VARCHAR(50) | UNIQUE, NOT NULL | 매장 식별자 (로그인 시 사용) |
| name | VARCHAR(100) | NOT NULL | 매장명 |
| address | VARCHAR(255) | NULLABLE | 매장 주소 |
| phone | VARCHAR(20) | NULLABLE | 매장 전화번호 |
| is_active | BOOLEAN | DEFAULT TRUE | 활성 상태 |
| created_at | DATETIME | NOT NULL | 생성 시각 |
| updated_at | DATETIME | NOT NULL | 수정 시각 |

**인덱스**: `store_code` (UNIQUE)

---

## 2. Admin (관리자)

| 필드 | 타입 | 제약조건 | 설명 |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | 관리자 고유 ID |
| store_id | BIGINT | FK → Store.id, NULLABLE | 소속 매장 (슈퍼 관리자는 NULL) |
| username | VARCHAR(50) | NOT NULL | 사용자명 |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt 해싱된 비밀번호 |
| role | ENUM('SUPER_ADMIN', 'STORE_ADMIN') | NOT NULL | 역할 |
| is_active | BOOLEAN | DEFAULT TRUE | 활성 상태 |
| created_at | DATETIME | NOT NULL | 생성 시각 |
| updated_at | DATETIME | NOT NULL | 수정 시각 |

**인덱스**: `(store_id, username)` (UNIQUE) - 동일 매장 내 사용자명 중복 방지
**관계**: Admin N:1 Store

---

## 3. Advertisement (광고)

| 필드 | 타입 | 제약조건 | 설명 |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | 광고 고유 ID |
| store_id | BIGINT | FK → Store.id, NOT NULL | 소속 매장 |
| image_path | VARCHAR(500) | NOT NULL | 이미지 파일 경로 |
| display_order | INT | NOT NULL, DEFAULT 0 | 노출 순서 |
| is_active | BOOLEAN | DEFAULT TRUE | 활성 상태 |
| created_at | DATETIME | NOT NULL | 생성 시각 |

**인덱스**: `(store_id, display_order)` - 매장별 순서 조회 최적화
**관계**: Advertisement N:1 Store

---

## 4. LoginAttempt (로그인 시도 기록)

| 필드 | 타입 | 제약조건 | 설명 |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | 기록 고유 ID |
| identifier | VARCHAR(100) | NOT NULL | 로그인 식별자 (username 또는 IP) |
| attempt_count | INT | NOT NULL, DEFAULT 0 | 연속 실패 횟수 |
| last_attempt_at | DATETIME | NOT NULL | 마지막 시도 시각 |
| locked_until | DATETIME | NULLABLE | 잠금 해제 시각 |

**인덱스**: `identifier` (INDEX)

---

## 5. ER 다이어그램

```
+------------------+       +------------------+
|     Store        |       |     Admin        |
+------------------+       +------------------+
| PK id            |<------| FK store_id      |
|    store_code    |       | PK id            |
|    name          |       |    username       |
|    address       |       |    password_hash  |
|    phone         |       |    role           |
|    is_active     |       |    is_active      |
|    created_at    |       |    created_at     |
|    updated_at    |       |    updated_at     |
+------------------+       +------------------+
        |
        |
        v
+------------------+       +------------------+
|  Advertisement   |       |  LoginAttempt    |
+------------------+       +------------------+
| PK id            |       | PK id            |
| FK store_id      |       |    identifier    |
|    image_path    |       |    attempt_count |
|    display_order |       |    last_attempt  |
|    is_active     |       |    locked_until  |
|    created_at    |       +------------------+
+------------------+
```

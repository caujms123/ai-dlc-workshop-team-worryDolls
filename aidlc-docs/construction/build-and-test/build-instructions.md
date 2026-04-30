# Build Instructions - Unit 4: 고객 UI + 테이블 관리

## Prerequisites

| 항목 | 요구 버전 |
|---|---|
| Python | 3.11+ |
| Node.js | 18+ |
| npm | 9+ |
| MySQL | 8.0+ |

## 환경 변수

`.env` 파일을 `backend/` 디렉토리에 생성:
```
DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/table_order
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=16
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=5242880
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
LOG_LEVEL=INFO
```

## Build Steps

### 1. MySQL 데이터베이스 생성
```bash
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS table_order CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 2. Backend 의존성 설치
```bash
cd backend
pip install -r requirements.txt
```

> `requirements.txt`가 아직 없다면 아래 패키지를 설치:
```bash
pip install fastapi uvicorn sqlalchemy aiomysql alembic python-jose passlib[bcrypt] python-multipart pydantic structlog slowapi httpx pytest pytest-asyncio
```

### 3. DB 마이그레이션 (Alembic 설정 후)
```bash
cd backend
alembic upgrade head
```

> Alembic 미설정 시 수동 테이블 생성:
```sql
CREATE TABLE table_info (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    store_id BIGINT NOT NULL,
    table_number INT NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    UNIQUE KEY uq_store_table_number (store_id, table_number)
);

CREATE TABLE table_session (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    table_id BIGINT NOT NULL,
    store_id BIGINT NOT NULL,
    started_at DATETIME NOT NULL,
    ended_at DATETIME NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    INDEX ix_table_session_active (table_id, is_active),
    FOREIGN KEY (table_id) REFERENCES table_info(id)
);
```

### 4. Backend 서버 실행
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 5. Customer Frontend 의존성 설치 및 실행
```bash
cd frontend/customer
npm install
npm run dev
```

### 6. 빌드 확인
- Backend API 문서: http://localhost:8000/docs
- Customer Frontend: http://localhost:5173

## Troubleshooting

### MySQL 연결 실패
- MySQL 서비스 실행 확인: `mysql -u root -p`
- DATABASE_URL 환경 변수 확인
- aiomysql 드라이버 설치 확인

### Frontend 빌드 실패
- Node.js 18+ 확인: `node --version`
- `node_modules` 삭제 후 재설치: `rm -rf node_modules && npm install`

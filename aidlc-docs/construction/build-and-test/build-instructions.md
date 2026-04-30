# Build Instructions - Unit 2: 메뉴 관리

## Prerequisites

| 항목 | 요구 버전 |
|---|---|
| **Python** | 3.11+ |
| **Node.js** | 18+ |
| **npm** | 9+ |
| **MySQL** | 8.0+ |

### 환경 변수

```bash
# .env 파일 (backend/ 디렉토리에 생성)
DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/table_order
JWT_SECRET_KEY=your-secret-key-change-in-production
UPLOAD_DIR=uploads
DEBUG=true
DATABASE_ECHO=false
CORS_ORIGINS=["http://localhost:5173","http://localhost:5174"]
```

---

## Build Steps

### 1. Database 준비

```bash
# MySQL 데이터베이스 생성
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS table_order CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 2. Backend 빌드

```bash
# 가상환경 생성 및 활성화
cd backend
python -m venv venv
source venv/bin/activate  # macOS/Linux

# 의존성 설치
pip install -r requirements.txt

# 테스트용 추가 의존성 (SQLite async)
pip install aiosqlite

# 업로드 디렉토리 생성
mkdir -p uploads/menus
```

### 3. Backend 서버 실행

```bash
cd backend
source venv/bin/activate
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**확인**: `http://localhost:8000/docs` 에서 Swagger UI 접근 가능

### 4. Admin Frontend 빌드

```bash
cd frontend/admin
npm install
npm run build
```

**개발 서버 실행**:
```bash
npm run dev
# http://localhost:5174 에서 접근
```

### 5. Customer Frontend 빌드

```bash
cd frontend/customer
npm install
npm run build
```

**개발 서버 실행**:
```bash
npm run dev
# http://localhost:5173 에서 접근
```

---

## Build Artifacts

| 산출물 | 경로 |
|---|---|
| Backend API | `http://localhost:8000` |
| API 문서 (Swagger) | `http://localhost:8000/docs` |
| Admin Frontend | `frontend/admin/dist/` |
| Customer Frontend | `frontend/customer/dist/` |
| 업로드 파일 | `uploads/` |

---

## Troubleshooting

### MySQL 연결 실패
- **원인**: MySQL 서비스 미실행 또는 인증 정보 불일치
- **해결**: `mysql.server start` 실행, `.env` 파일의 DATABASE_URL 확인

### aiomysql 설치 실패
- **원인**: MySQL 클라이언트 라이브러리 미설치
- **해결**: `brew install mysql-client` (macOS)

### Frontend 빌드 실패
- **원인**: Node.js 버전 불일치
- **해결**: `node -v`로 18+ 확인, `nvm use 18` 등으로 전환

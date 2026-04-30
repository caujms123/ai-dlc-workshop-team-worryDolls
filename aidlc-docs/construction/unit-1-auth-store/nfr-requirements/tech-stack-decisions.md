# Unit 1: Tech Stack Decisions - 인증 + 매장 + 관리자 + 광고

---

## Backend Tech Stack

| 영역 | 기술 | 버전 | 선택 이유 |
|---|---|---|---|
| **Runtime** | Python | 3.11+ | FastAPI 호환, 안정적 |
| **Framework** | FastAPI | 0.104+ | 비동기 지원, 자동 API 문서, Pydantic 통합 |
| **ORM** | SQLAlchemy | 2.0+ | Python 표준 ORM, 비동기 지원 |
| **DB** | MySQL | 8.0+ | 사용자 선택, 안정적 RDBMS |
| **DB Driver** | aiomysql | 0.2+ | 비동기 MySQL 드라이버 |
| **Migration** | Alembic | 1.12+ | SQLAlchemy 공식 마이그레이션 도구 |
| **인증** | python-jose | 3.3+ | JWT 토큰 생성/검증 |
| **해싱** | passlib[bcrypt] | 1.7+ | bcrypt 해싱 |
| **검증** | Pydantic | 2.0+ | FastAPI 내장, 입력 검증 |
| **파일 업로드** | python-multipart | 0.0.6+ | FastAPI 파일 업로드 지원 |
| **CORS** | FastAPI CORSMiddleware | 내장 | CORS 정책 설정 |
| **로깅** | Python logging + structlog | 23.0+ | 구조화된 JSON 로깅 |
| **테스트** | pytest + httpx | 최신 | FastAPI 테스트 표준 |
| **Rate Limiting** | slowapi | 0.1+ | FastAPI Rate Limiting |

## Frontend Tech Stack (Admin)

| 영역 | 기술 | 버전 | 선택 이유 |
|---|---|---|---|
| **Framework** | Vue.js | 3.x | 사용자 선택 |
| **Build Tool** | Vite | 5.x | Vue 3 공식 빌드 도구 |
| **상태 관리** | Pinia | 2.x | Vue 3 공식 상태 관리 |
| **라우터** | Vue Router | 4.x | Vue 3 공식 라우터 |
| **HTTP Client** | Axios | 1.x | HTTP 요청 라이브러리 |
| **UI 컴포넌트** | 자체 구현 | - | 커스텀 디자인 |
| **테스트** | Vitest | 1.x | Vite 기반 테스트 |

## 공통 설정

### 환경 변수
```
DATABASE_URL=mysql+aiomysql://user:pass@localhost:3306/table_order
JWT_SECRET_KEY=<random-256-bit-key>
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=16
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=5242880  # 5MB
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
LOG_LEVEL=INFO
```

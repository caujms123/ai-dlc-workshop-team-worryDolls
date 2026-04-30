# 테이블오더 서비스 - Application Design 통합 문서

---

## 1. 시스템 개요

테이블오더 서비스는 3-tier 아키텍처로 구성됩니다:
- **Frontend**: Vue.js (Customer UI + Admin UI)
- **Backend**: Python FastAPI (REST API + SSE)
- **Database**: MySQL (SQLAlchemy ORM)

---

## 2. Backend 컴포넌트 (10개)

| # | 컴포넌트 | 목적 | 주요 API |
|---|---|---|---|
| 1 | AuthComponent | 인증/인가 | 로그인, JWT, RBAC |
| 2 | StoreComponent | 매장 관리 | 매장 CRUD |
| 3 | AdminComponent | 관리자 계정 | 관리자 CRUD |
| 4 | AdvertisementComponent | 광고 관리 | 광고 이미지 CRUD |
| 5 | CategoryComponent | 카테고리 관리 | 카테고리 CRUD |
| 6 | MenuComponent | 메뉴 관리 | 메뉴 CRUD + 이미지 |
| 7 | TableComponent | 테이블/세션 | 테이블 설정, 세션 관리 |
| 8 | OrderComponent | 주문 처리 | 주문 CRUD + 이력 |
| 9 | SSEComponent | 실시간 이벤트 | SSE 스트림 |
| 10 | FileUploadComponent | 파일 업로드 | 이미지 업로드 공통 |

> 상세: `components.md`, `component-methods.md`

---

## 3. 서비스 레이어 아키텍처

```
API Routers → Middleware (Auth, RateLimit, Error) → Services → Repositories → MySQL
                                                       |
                                                       v
                                                  SSE (실시간)
```

**미들웨어**: AuthMiddleware (JWT/RBAC), RateLimiter, GlobalErrorHandler
**통신**: REST (동기) + SSE (비동기 실시간)

> 상세: `services.md`

---

## 4. Frontend 컴포넌트

### Customer UI (8개 컴포넌트)
AdScreen, MenuBrowser, CartManager, PaymentSelector, LadderGame, OrderConfirm, OrderHistory, TableAuth

### Admin UI (9개 컴포넌트)
AdminLogin, StoreDashboard, StoreManager, AdminManager, AdManager, MenuManager, OrderMonitor, OrderDetail, TableManager

> 상세: `components.md`

---

## 5. 핵심 의존성

- OrderService가 가장 많은 의존성 보유 (Table, Menu, SSE)
- FileUploadService는 Advertisement, Menu에서 공유
- SSEService는 독립적이며 Order에서 이벤트 발행
- 순환 의존성 주의: OrderService ↔ TableService (Repository 직접 접근으로 해결)

> 상세: `component-dependency.md`

---

## 6. API 엔드포인트 요약

| 도메인 | 엔드포인트 수 | 인증 수준 |
|---|---|---|
| Auth | 5 | Public (로그인), Authenticated (나머지) |
| Store | 4 | SUPER_ADMIN |
| Admin | 4 | SUPER_ADMIN |
| Advertisement | 6 | SUPER_ADMIN (관리), Public (고객 조회) |
| Category | 4 | STORE_ADMIN |
| Menu | 7 | STORE_ADMIN (관리), Public (고객 조회) |
| Table | 4 | STORE_ADMIN |
| Order | 6 | STORE_ADMIN (관리), TABLE (생성/조회) |
| SSE | 2 | STORE_ADMIN, TABLE |
| File Upload | 1 | Authenticated |
| **합계** | **43** | |

---

## 7. 데이터 모델 엔티티 (10개)

Store, Admin, Advertisement, Category, Menu, TableInfo, TableSession, Order, OrderItem, OrderHistory

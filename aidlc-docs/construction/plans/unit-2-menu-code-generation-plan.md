# Unit 2: 메뉴 관리 - Code Generation Plan

> **Unit**: Unit 2 - 메뉴 관리 (개발자 B)
> **도메인**: Category CRUD, Menu CRUD, 고객용 메뉴 조회
> **기술 스택**: Python + FastAPI (Backend), Vue.js 3 + Vite + Pinia (Frontend)

---

## Unit Context

### 담당 User Stories
| Story ID | 제목 | 페르소나 |
|---|---|---|
| US-MA-02 | 메뉴 조회 | 매장 관리자 |
| US-MA-03 | 메뉴 등록 | 매장 관리자 |
| US-MA-04 | 메뉴 수정 | 매장 관리자 |
| US-MA-05 | 메뉴 삭제 | 매장 관리자 |
| US-MA-06 | 메뉴 노출 순서 조정 | 매장 관리자 |
| US-CU-04 | 카테고리별 메뉴 조회 | 고객 |

### Unit 1 의존성 (개발자 A 제공)
- `AuthMiddleware` (JWT 검증, RBAC)
- `FileUploadService` (이미지 업로드/삭제)
- `GlobalErrorHandler` (전역 에러 처리)
- `database.py` (DB 세션 관리)
- `config.py` (설정)
- Store 모델 (FK 참조)

### 소유 엔티티
- Category (카테고리)
- Menu (메뉴)

### API 엔드포인트
- `POST /api/stores/{store_id}/categories` - 카테고리 등록
- `GET /api/stores/{store_id}/categories` - 카테고리 목록 조회
- `PUT /api/categories/{category_id}` - 카테고리 수정
- `DELETE /api/categories/{category_id}` - 카테고리 삭제
- `POST /api/stores/{store_id}/menus` - 메뉴 등록
- `GET /api/stores/{store_id}/menus` - 메뉴 목록 조회
- `GET /api/menus/{menu_id}` - 메뉴 상세 조회
- `PUT /api/menus/{menu_id}` - 메뉴 수정
- `DELETE /api/menus/{menu_id}` - 메뉴 삭제
- `PUT /api/menus/{menu_id}/order` - 노출 순서 변경
- `GET /api/customer/stores/{store_id}/menus` - 고객용 메뉴 조회

---

## Code Generation Steps

### Step 1: Project Structure Setup (Greenfield 공통 구조)
- [x] `backend/` 디렉토리 구조 생성 (app/, tests/)
- [x] `backend/requirements.txt` 생성 (의존성 정의)
- [x] `backend/app/__init__.py` 생성
- [x] `backend/app/config.py` 생성 (환경 설정)
- [x] `backend/app/database.py` 생성 (SQLAlchemy 세션 관리)
- [x] `backend/app/main.py` 생성 (FastAPI 앱 진입점, 라우터 등록)
- [x] `frontend/customer/` Vue.js 프로젝트 초기 구조 생성
- [x] `frontend/admin/` Vue.js 프로젝트 초기 구조 생성

> **Note**: Unit 1이 공통 구조를 먼저 생성할 수 있으나, Unit 2가 독립적으로 작업할 수 있도록 필요한 기반 파일을 포함합니다. 충돌 시 Unit 1의 구현을 우선합니다.

### Step 2: Database Models (SQLAlchemy)
- [x] `backend/app/models/__init__.py` 생성
- [x] `backend/app/models/category.py` - Category 모델 정의
- [x] `backend/app/models/menu.py` - Menu 모델 정의
- [x] 인덱스 정의: `(store_id, display_order)`, `(store_id, category_id, display_order)`

**Story 매핑**: US-MA-02, US-MA-03 (데이터 모델 기반)

### Step 3: Pydantic Schemas
- [x] `backend/app/schemas/__init__.py` 생성
- [x] `backend/app/schemas/category.py` - CategoryCreate, CategoryUpdate, CategoryResponse 스키마
- [x] `backend/app/schemas/menu.py` - MenuCreate, MenuUpdate, MenuResponse, CustomerMenuResponse 스키마
- [x] 입력 검증 규칙 적용 (name 2~100자, price 0~10,000,000 등)

**Story 매핑**: US-MA-03 (필수 필드 검증), US-MA-04 (수정 검증)

### Step 4: Repository Layer
- [x] `backend/app/repositories/__init__.py` 생성
- [x] `backend/app/repositories/category_repo.py` - CategoryRepository 구현
  - `get_by_store()`, `get_by_id()`, `create()`, `update()`, `delete()`, `reorder()`
- [x] `backend/app/repositories/menu_repo.py` - MenuRepository 구현
  - `get_by_store()`, `get_by_category()`, `get_available_by_store()`, `get_by_id()`, `create()`, `update()`, `delete()`, `reorder()`

**Story 매핑**: 전체 (데이터 접근 계층)

### Step 5: Repository Layer Unit Tests
- [x] `backend/tests/__init__.py` 생성
- [x] `backend/tests/conftest.py` - 테스트 DB 설정, fixtures
- [x] `backend/tests/test_category_repo.py` - CategoryRepository 단위 테스트
- [x] `backend/tests/test_menu_repo.py` - MenuRepository 단위 테스트

### Step 6: Service Layer (Business Logic)
- [x] `backend/app/services/__init__.py` 생성
- [x] `backend/app/services/category_service.py` - CategoryService 구현
  - `create_category()`, `get_categories()`, `update_category()`, `delete_category()`
  - BR-CAT-01: 카테고리 생성 규칙 (display_order 자동 할당)
  - BR-CAT-02: 카테고리 삭제 규칙 (메뉴 존재 시 409)
- [x] `backend/app/services/menu_service.py` - MenuService 구현
  - `create_menu()`, `get_menus()`, `get_menu()`, `update_menu()`, `delete_menu()`, `update_menu_order()`, `get_customer_menus()`
  - BR-MENU-01~05: 메뉴 비즈니스 규칙 전체 적용
  - FileUploadService 연동 (이미지 업로드/교체/삭제)

**Story 매핑**: US-MA-02~06 (관리자 메뉴 관리), US-CU-04 (고객 메뉴 조회)

### Step 7: Service Layer Unit Tests
- [x] `backend/tests/test_category_service.py` - CategoryService 단위 테스트
  - 카테고리 CRUD 테스트
  - 메뉴 존재 시 삭제 거부 테스트 (BR-CAT-02)
- [x] `backend/tests/test_menu_service.py` - MenuService 단위 테스트
  - 메뉴 CRUD 테스트
  - 가격 검증 테스트 (BR-MENU-02)
  - 이미지 교체 테스트 (BR-MENU-03)
  - 고객용 메뉴 조회 테스트 (BR-MENU-05)

### Step 8: API Router Layer
- [x] `backend/app/routers/__init__.py` 생성
- [x] `backend/app/routers/category.py` - Category API 라우터
  - `POST /api/stores/{store_id}/categories`
  - `GET /api/stores/{store_id}/categories`
  - `PUT /api/categories/{category_id}`
  - `DELETE /api/categories/{category_id}`
  - AuthMiddleware 적용 (STORE_ADMIN 역할)
  - 매장 스코프 검증
- [x] `backend/app/routers/menu.py` - Menu API 라우터
  - `POST /api/stores/{store_id}/menus` (multipart/form-data)
  - `GET /api/stores/{store_id}/menus`
  - `GET /api/menus/{menu_id}`
  - `PUT /api/menus/{menu_id}` (multipart/form-data)
  - `DELETE /api/menus/{menu_id}`
  - `PUT /api/menus/{menu_id}/order`
  - `GET /api/customer/stores/{store_id}/menus` (고객용)
  - AuthMiddleware 적용 (관리자: STORE_ADMIN, 고객: TABLE)

**Story 매핑**: US-MA-02~06, US-CU-04

### Step 9: API Router Layer Unit Tests
- [x] `backend/tests/test_category_router.py` - Category API 통합 테스트
  - CRUD 엔드포인트 테스트
  - 권한 검증 테스트 (비인증, 다른 매장)
  - 입력 검증 테스트
- [x] `backend/tests/test_menu_router.py` - Menu API 통합 테스트
  - CRUD 엔드포인트 테스트
  - 이미지 업로드 테스트
  - 고객용 메뉴 조회 테스트
  - 권한 검증 테스트

### Step 10: Admin Frontend - MenuManager
- [x] `frontend/admin/src/services/menuApi.js` - 메뉴/카테고리 API 호출 서비스
- [x] `frontend/admin/src/stores/menuStore.js` - Pinia 메뉴 상태 관리
- [x] `frontend/admin/src/views/MenuView.vue` - 메뉴 관리 메인 화면
- [x] `frontend/admin/src/components/menu/CategoryList.vue` - 카테고리 목록 (좌측 패널)
- [x] `frontend/admin/src/components/menu/CategoryForm.vue` - 카테고리 등록/수정 모달
- [x] `frontend/admin/src/components/menu/MenuList.vue` - 메뉴 목록 (우측 패널)
- [x] `frontend/admin/src/components/menu/MenuForm.vue` - 메뉴 등록/수정 모달 (이미지 업로드 포함)
- [x] `frontend/admin/src/components/menu/MenuCard.vue` - 메뉴 카드 (수정/삭제/순서 변경)
- [x] 라우터 설정에 `/menu` 경로 추가

**Story 매핑**: US-MA-02 (조회), US-MA-03 (등록), US-MA-04 (수정), US-MA-05 (삭제), US-MA-06 (순서 조정)

### Step 11: Admin Frontend Unit Tests
- [x] `frontend/admin/src/components/menu/__tests__/CategoryList.spec.js` - 카테고리 목록 테스트
- [x] `frontend/admin/src/components/menu/__tests__/MenuForm.spec.js` - 메뉴 폼 테스트
- [x] `frontend/admin/src/components/menu/__tests__/MenuCard.spec.js` - 메뉴 카드 테스트
- [x] `frontend/admin/src/stores/__tests__/menuStore.spec.js` - Pinia 스토어 테스트

### Step 12: Customer Frontend - MenuBrowser
- [x] `frontend/customer/src/services/menuApi.js` - 고객용 메뉴 API 호출 서비스
- [x] `frontend/customer/src/stores/menuStore.js` - Pinia 메뉴 상태 관리
- [x] `frontend/customer/src/views/MenuView.vue` - 메뉴 탐색 메인 화면
- [x] `frontend/customer/src/components/menu/CategoryTabs.vue` - 카테고리 탭 (상단, 가로 스크롤)
- [x] `frontend/customer/src/components/menu/MenuGrid.vue` - 메뉴 카드 그리드 (2열)
- [x] `frontend/customer/src/components/menu/MenuCard.vue` - 메뉴 카드 (이미지, 이름, 가격)
- [x] `frontend/customer/src/components/menu/MenuDetail.vue` - 메뉴 상세 팝업 (장바구니 추가)
- [x] 라우터 설정에 `/menu` 경로 추가
- [x] 이미지 lazy loading 적용
- [x] 터치 타겟 최소 44x44px 보장

**Story 매핑**: US-CU-04 (카테고리별 메뉴 조회)

### Step 13: Customer Frontend Unit Tests
- [x] `frontend/customer/src/components/menu/__tests__/CategoryTabs.spec.js` - 카테고리 탭 테스트
- [x] `frontend/customer/src/components/menu/__tests__/MenuCard.spec.js` - 메뉴 카드 테스트
- [x] `frontend/customer/src/components/menu/__tests__/MenuDetail.spec.js` - 메뉴 상세 테스트
- [x] `frontend/customer/src/stores/__tests__/menuStore.spec.js` - Pinia 스토어 테스트

### Step 14: Documentation & Summary
- [x] `aidlc-docs/construction/unit-2-menu/code/backend-summary.md` - Backend 코드 요약
- [x] `aidlc-docs/construction/unit-2-menu/code/frontend-summary.md` - Frontend 코드 요약
- [x] `aidlc-docs/construction/unit-2-menu/code/api-documentation.md` - API 문서

---

## Story Completion Tracking

| Story ID | 제목 | 구현 Step | 완료 |
|---|---|---|---|
| US-MA-02 | 메뉴 조회 | Step 2~10 | [x] |
| US-MA-03 | 메뉴 등록 | Step 2~10 | [x] |
| US-MA-04 | 메뉴 수정 | Step 6~10 | [x] |
| US-MA-05 | 메뉴 삭제 | Step 6~10 | [x] |
| US-MA-06 | 메뉴 노출 순서 조정 | Step 6~10 | [x] |
| US-CU-04 | 카테고리별 메뉴 조회 | Step 2~12 | [x] |

---

## Security Extension Compliance Plan

| 규칙 | 적용 방식 |
|---|---|
| SECURITY-05 (입력 검증) | Pydantic 스키마, 가격/길이 검증, 파라미터화된 쿼리 |
| SECURITY-08 (접근 제어) | AuthMiddleware, STORE_ADMIN 역할 검증, 매장 스코프 |
| SECURITY-09 (보안 강화) | 프로덕션 에러 메시지 제네릭화, 스택 트레이스 숨김 |
| SECURITY-10 (공급망) | requirements.txt 정확한 버전 고정 |
| SECURITY-15 (예외 처리) | try/except, 리소스 정리, fail-closed |
| SECURITY-03 (로깅) | 구조화된 로깅, 민감 데이터 제외 |
| SECURITY-11 (보안 설계) | 보안 로직 분리 (AuthMiddleware), 계층 방어 |

---

## Total Steps: 14
## Estimated Files: ~40+ files (Backend ~20, Frontend Admin ~10, Frontend Customer ~10, Tests ~15, Docs ~3)

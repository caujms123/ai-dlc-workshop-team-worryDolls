# 테이블오더 서비스 - Unit of Work 정의

> **팀 구성**: 4명 (1인 1 Unit)
> **분배 원칙**: 도메인 응집도 기반, Backend + 관련 Frontend를 하나의 Unit으로 묶어 Full-stack 작업 단위 구성
> **크기 원칙**: 각 Unit이 비슷한 작업량을 갖도록 균형 배분

---

## Unit 분배 개요

| Unit | 담당자 | 도메인 | Backend 컴포넌트 | Frontend 컴포넌트 | 스토리 수 |
|---|---|---|---|---|---|
| **Unit 1** | 개발자 A | 인증 + 매장 + 관리자 + 광고 | Auth, Store, Admin, Advertisement, FileUpload | AdminLogin, StoreDashboard, StoreManager, AdminManager, AdManager | SA: 7개 |
| **Unit 2** | 개발자 B | 메뉴 관리 | Category, Menu | MenuManager (Admin), MenuBrowser (Customer) | MA: 5개, CU: 1개 |
| **Unit 3** | 개발자 C | 주문 + 실시간 모니터링 | Order, SSE | OrderMonitor, OrderDetail, OrderConfirm, OrderHistory (Customer) | MA: 7개, CU: 2개 |
| **Unit 4** | 개발자 D | 고객 UI + 테이블 관리 | Table | AdScreen, CartManager, PaymentSelector, LadderGame, TableAuth (Customer), TableManager (Admin) | MA: 4개, CU: 5개 |

---

## Unit 1: 인증 + 매장 + 관리자 + 광고 (개발자 A)

### 범위
**Backend**:
- AuthService (JWT 발급/검증, bcrypt, 로그인 시도 제한, RBAC)
- AuthMiddleware, RateLimiter, GlobalErrorHandler
- StoreService (매장 CRUD)
- AdminService (관리자 계정 CRUD)
- AdvertisementService (광고 이미지 CRUD)
- FileUploadService (이미지 업로드 공통 모듈)
- DB 모델: Store, Admin, Advertisement

**Frontend (Admin)**:
- AdminLogin (슈퍼/매장 관리자 로그인)
- StoreDashboard (매장 관리 대시보드)
- StoreManager (매장 CRUD)
- AdminManager (관리자 계정 관리)
- AdManager (광고 이미지 관리)

### 관련 User Stories
US-SA-01 ~ US-SA-07 (슈퍼 관리자 전체)

### 산출물
- 인증 미들웨어 및 JWT 유틸리티
- 매장/관리자/광고 REST API
- 파일 업로드 공통 모듈
- 관리자 로그인 및 매장 관리 UI
- 글로벌 에러 핸들러

### 왜 이 조합인가
- 인증은 모든 Unit의 기반이므로 가장 먼저 완성되어야 함
- Store, Admin은 인증과 밀접하게 연관 (로그인 시 매장/관리자 검증)
- Advertisement는 FileUpload를 공유하며 Store에 종속
- 미들웨어(Auth, RateLimit, Error)는 다른 Unit에서도 사용하므로 공통 기반 역할

---

## Unit 2: 메뉴 관리 (개발자 B)

### 범위
**Backend**:
- CategoryService (카테고리 CRUD)
- MenuService (메뉴 CRUD, 이미지 업로드, 순서 조정)
- DB 모델: Category, Menu

**Frontend (Admin)**:
- MenuManager (메뉴 CRUD, 이미지 업로드, 카테고리 관리, 순서 조정)

**Frontend (Customer)**:
- MenuBrowser (카테고리별 메뉴 탐색, 카드 레이아웃, 메뉴 상세)

### 관련 User Stories
US-MA-02 ~ US-MA-06 (메뉴 관리), US-CU-04 (메뉴 조회)

### 산출물
- 카테고리/메뉴 REST API
- 메뉴 이미지 업로드 (FileUploadService 활용 - Unit 1 제공)
- 관리자 메뉴 관리 UI
- 고객 메뉴 탐색 UI

### 왜 이 조합인가
- 메뉴는 독립적인 도메인으로 다른 Unit과 의존성이 적음
- 관리자 메뉴 관리 + 고객 메뉴 조회를 한 사람이 담당하면 데이터 일관성 보장
- FileUploadService는 Unit 1에서 제공하는 공통 모듈 활용

---

## Unit 3: 주문 + 실시간 모니터링 (개발자 C)

### 범위
**Backend**:
- OrderService (주문 생성, 상태 변경, 삭제, 이력 관리, 총 주문액)
- SSEService (실시간 이벤트 스트리밍)
- DB 모델: Order, OrderItem, OrderHistory

**Frontend (Admin)**:
- OrderMonitor (실시간 주문 대시보드, 그리드 레이아웃, SSE)
- OrderDetail (주문 상세 보기, 상태 변경, 주문 삭제)

**Frontend (Customer)**:
- OrderConfirm (주문 확정 화면, 주문 성공/실패)
- OrderHistory (주문 내역 조회, SSE 실시간 상태 업데이트)

### 관련 User Stories
US-MA-07 ~ US-MA-09 (주문 모니터링), US-MA-11 (주문 삭제), US-MA-12 ~ US-MA-13 (이용 완료, 과거 내역), US-CU-09 (주문 확정), US-CU-10 (주문 내역)

### 산출물
- 주문 REST API
- SSE 엔드포인트 (관리자 + 고객)
- 관리자 주문 모니터링 대시보드 UI
- 고객 주문 확정 및 내역 UI

### 왜 이 조합인가
- 주문과 SSE는 밀접하게 연관 (주문 생성 → SSE 이벤트 발행)
- 관리자 모니터링과 고객 주문 내역 모두 SSE를 사용
- 주문 이력 관리(이용 완료 시 이동)도 주문 도메인에 포함

---

## Unit 4: 고객 UI + 테이블 관리 (개발자 D)

### 범위
**Backend**:
- TableService (테이블 설정, 세션 라이프사이클, 이용 완료)
- DB 모델: TableInfo, TableSession

**Frontend (Customer)**:
- AdScreen (광고 화면, 5초 자동 슬라이드, 터치 시 메뉴 이동)
- CartManager (장바구니 관리, 로컬 저장, 수량 조절)
- PaymentSelector (결제 방식 선택 팝업: 더치페이/단독)
- LadderGame (사다리 타기 미니게임: 인원 선택, 애니메이션, 효과음, 결과 강조)
- TableAuth (테이블 초기 설정, 자동 로그인)

**Frontend (Admin)**:
- TableManager (테이블 설정, 이용 완료, 과거 내역 조회)

### 관련 User Stories
US-MA-10 (테이블 설정), US-MA-12 (이용 완료 - Unit 3과 협업), US-CU-01 ~ US-CU-03 (자동 로그인, 광고, 메뉴 이동), US-CU-05 ~ US-CU-08 (장바구니, 결제 선택, 사다리 타기)

### 산출물
- 테이블/세션 REST API
- 광고 화면 (슬라이드)
- 장바구니 (로컬 저장)
- 결제 방식 선택 팝업
- 사다리 타기 미니게임 (풍부한 UX)
- 테이블 인증 (자동 로그인)
- 관리자 테이블 관리 UI

### 왜 이 조합인가
- 고객 여정의 시작(광고→메뉴 이동)과 중간(장바구니→결제 선택→사다리)을 담당
- 테이블 세션 관리는 고객 인증과 직결
- 사다리 타기 미니게임은 독립적인 Frontend 작업으로 병렬 개발에 적합
- Backend 작업량이 적은 대신 Frontend 작업량(특히 사다리 타기)이 많아 균형 맞춤

---

## 작업량 균형 분석

| Unit | Backend 서비스 | API 수 | Frontend 컴포넌트 | 스토리 수 | 난이도 |
|---|---|---|---|---|---|
| Unit 1 | 5 (Auth, Store, Admin, Ad, FileUpload) + 미들웨어 3 | 20 | 5 | 7 | ★★★★ (인증 복잡도) |
| Unit 2 | 2 (Category, Menu) | 11 | 2 | 6 | ★★★ (CRUD + 이미지) |
| Unit 3 | 2 (Order, SSE) | 8 | 4 | 9 | ★★★★ (SSE + 이력 관리) |
| Unit 4 | 1 (Table) | 4 | 6 | 9 | ★★★★ (사다리 타기 UX) |

---

## 코드 구조 (Greenfield)

```
table-order-service/
+-- backend/                          # FastAPI Backend
|   +-- app/
|   |   +-- main.py                   # FastAPI 앱 진입점
|   |   +-- config.py                 # 설정
|   |   +-- database.py               # DB 연결
|   |   +-- middleware/               # [Unit 1]
|   |   |   +-- auth.py
|   |   |   +-- rate_limiter.py
|   |   |   +-- error_handler.py
|   |   +-- models/                   # SQLAlchemy 모델
|   |   |   +-- store.py              # [Unit 1]
|   |   |   +-- admin.py              # [Unit 1]
|   |   |   +-- advertisement.py      # [Unit 1]
|   |   |   +-- category.py           # [Unit 2]
|   |   |   +-- menu.py               # [Unit 2]
|   |   |   +-- order.py              # [Unit 3]
|   |   |   +-- table.py              # [Unit 4]
|   |   +-- routers/                  # API 라우터
|   |   |   +-- auth.py               # [Unit 1]
|   |   |   +-- store.py              # [Unit 1]
|   |   |   +-- admin.py              # [Unit 1]
|   |   |   +-- advertisement.py      # [Unit 1]
|   |   |   +-- category.py           # [Unit 2]
|   |   |   +-- menu.py               # [Unit 2]
|   |   |   +-- order.py              # [Unit 3]
|   |   |   +-- sse.py                # [Unit 3]
|   |   |   +-- table.py              # [Unit 4]
|   |   +-- services/                 # 비즈니스 로직
|   |   |   +-- auth_service.py       # [Unit 1]
|   |   |   +-- store_service.py      # [Unit 1]
|   |   |   +-- admin_service.py      # [Unit 1]
|   |   |   +-- ad_service.py         # [Unit 1]
|   |   |   +-- file_upload_service.py# [Unit 1]
|   |   |   +-- category_service.py   # [Unit 2]
|   |   |   +-- menu_service.py       # [Unit 2]
|   |   |   +-- order_service.py      # [Unit 3]
|   |   |   +-- sse_service.py        # [Unit 3]
|   |   |   +-- table_service.py      # [Unit 4]
|   |   +-- repositories/            # 데이터 접근
|   |   |   +-- store_repo.py         # [Unit 1]
|   |   |   +-- admin_repo.py         # [Unit 1]
|   |   |   +-- ad_repo.py            # [Unit 1]
|   |   |   +-- category_repo.py      # [Unit 2]
|   |   |   +-- menu_repo.py          # [Unit 2]
|   |   |   +-- order_repo.py         # [Unit 3]
|   |   |   +-- table_repo.py         # [Unit 4]
|   |   +-- schemas/                  # Pydantic 스키마
|   |   |   +-- auth.py               # [Unit 1]
|   |   |   +-- store.py              # [Unit 1]
|   |   |   +-- admin.py              # [Unit 1]
|   |   |   +-- advertisement.py      # [Unit 1]
|   |   |   +-- category.py           # [Unit 2]
|   |   |   +-- menu.py               # [Unit 2]
|   |   |   +-- order.py              # [Unit 3]
|   |   |   +-- table.py              # [Unit 4]
|   |   +-- utils/                    # 유틸리티
|   |       +-- security.py           # [Unit 1]
|   |       +-- file_utils.py         # [Unit 1]
|   +-- tests/                        # 테스트
|   |   +-- test_auth.py              # [Unit 1]
|   |   +-- test_store.py             # [Unit 1]
|   |   +-- test_admin.py             # [Unit 1]
|   |   +-- test_advertisement.py     # [Unit 1]
|   |   +-- test_category.py          # [Unit 2]
|   |   +-- test_menu.py              # [Unit 2]
|   |   +-- test_order.py             # [Unit 3]
|   |   +-- test_sse.py               # [Unit 3]
|   |   +-- test_table.py             # [Unit 4]
|   +-- requirements.txt
|   +-- alembic/                      # DB 마이그레이션
|
+-- frontend/
|   +-- customer/                     # 고객용 Vue.js 앱
|   |   +-- src/
|   |   |   +-- views/
|   |   |   |   +-- AdScreen.vue      # [Unit 4]
|   |   |   |   +-- MenuView.vue      # [Unit 2]
|   |   |   |   +-- CartView.vue      # [Unit 4]
|   |   |   |   +-- OrderView.vue     # [Unit 3]
|   |   |   |   +-- OrderHistoryView.vue # [Unit 3]
|   |   |   |   +-- TableAuthView.vue # [Unit 4]
|   |   |   +-- components/
|   |   |   |   +-- MenuCard.vue      # [Unit 2]
|   |   |   |   +-- CartItem.vue      # [Unit 4]
|   |   |   |   +-- PaymentSelector.vue # [Unit 4]
|   |   |   |   +-- LadderGame.vue    # [Unit 4]
|   |   |   |   +-- OrderConfirm.vue  # [Unit 3]
|   |   |   +-- stores/               # Pinia 상태 관리
|   |   |   +-- services/             # API 호출
|   |   |   +-- router/
|   |
|   +-- admin/                        # 관리자용 Vue.js 앱
|       +-- src/
|           +-- views/
|           |   +-- LoginView.vue     # [Unit 1]
|           |   +-- StoreView.vue     # [Unit 1]
|           |   +-- AdminView.vue     # [Unit 1]
|           |   +-- AdView.vue        # [Unit 1]
|           |   +-- MenuView.vue      # [Unit 2]
|           |   +-- OrderView.vue     # [Unit 3]
|           |   +-- TableView.vue     # [Unit 4]
|           +-- components/
|           +-- stores/
|           +-- services/
|           +-- router/
```

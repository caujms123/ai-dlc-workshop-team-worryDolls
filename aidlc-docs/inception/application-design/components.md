# 테이블오더 서비스 - 컴포넌트 정의

---

## 1. Backend 컴포넌트 (FastAPI)

### 1.1 AuthComponent
**목적**: 인증 및 인가 처리
**책임**:
- 슈퍼 관리자, 매장 관리자, 테이블 태블릿 로그인 처리
- JWT 토큰 발급 및 검증
- 비밀번호 해싱 (bcrypt)
- 로그인 시도 제한 (brute-force 방지)
- 역할 기반 접근 제어 (RBAC)
- 세션 만료 관리 (16시간)

**인터페이스**:
- `POST /api/auth/admin/login` - 관리자 로그인
- `POST /api/auth/table/login` - 테이블 태블릿 로그인
- `POST /api/auth/table/auto-login` - 테이블 자동 로그인
- `POST /api/auth/logout` - 로그아웃
- `GET /api/auth/me` - 현재 사용자 정보

---

### 1.2 StoreComponent
**목적**: 매장 정보 관리
**책임**:
- 매장 CRUD (슈퍼 관리자 전용)
- 매장 식별자 고유성 검증
- 매장별 데이터 격리 기반 제공

**인터페이스**:
- `POST /api/stores` - 매장 등록
- `GET /api/stores` - 매장 목록 조회
- `GET /api/stores/{store_id}` - 매장 상세 조회
- `PUT /api/stores/{store_id}` - 매장 수정

---

### 1.3 AdminComponent
**목적**: 관리자 계정 관리
**책임**:
- 매장별 관리자 계정 CRUD (슈퍼 관리자 전용)
- 관리자 계정 활성/비활성 관리
- 사용자명 중복 검증

**인터페이스**:
- `POST /api/stores/{store_id}/admins` - 관리자 생성
- `GET /api/stores/{store_id}/admins` - 관리자 목록 조회
- `PUT /api/admins/{admin_id}` - 관리자 수정
- `PATCH /api/admins/{admin_id}/status` - 관리자 활성/비활성

---

### 1.4 AdvertisementComponent
**목적**: 광고 이미지 관리
**책임**:
- 매장별 광고 이미지 업로드/삭제
- 광고 이미지 노출 순서 관리
- 광고 활성/비활성 관리
- 고객용 활성 광고 목록 제공

**인터페이스**:
- `POST /api/stores/{store_id}/advertisements` - 광고 이미지 업로드
- `GET /api/stores/{store_id}/advertisements` - 광고 목록 조회
- `DELETE /api/advertisements/{ad_id}` - 광고 삭제
- `PUT /api/advertisements/{ad_id}/order` - 노출 순서 변경
- `PATCH /api/advertisements/{ad_id}/status` - 활성/비활성 전환
- `GET /api/customer/stores/{store_id}/advertisements` - 고객용 활성 광고 조회

---

### 1.5 CategoryComponent
**목적**: 메뉴 카테고리 관리
**책임**:
- 매장별 카테고리 CRUD
- 카테고리 순서 관리

**인터페이스**:
- `POST /api/stores/{store_id}/categories` - 카테고리 등록
- `GET /api/stores/{store_id}/categories` - 카테고리 목록 조회
- `PUT /api/categories/{category_id}` - 카테고리 수정
- `DELETE /api/categories/{category_id}` - 카테고리 삭제

---

### 1.6 MenuComponent
**목적**: 메뉴 항목 관리
**책임**:
- 메뉴 CRUD (매장 관리자)
- 메뉴 이미지 파일 업로드
- 메뉴 노출 순서 관리
- 필수 필드 및 가격 범위 검증
- 고객용 메뉴 조회 제공

**인터페이스**:
- `POST /api/stores/{store_id}/menus` - 메뉴 등록 (이미지 포함)
- `GET /api/stores/{store_id}/menus` - 메뉴 목록 조회 (카테고리별)
- `GET /api/menus/{menu_id}` - 메뉴 상세 조회
- `PUT /api/menus/{menu_id}` - 메뉴 수정
- `DELETE /api/menus/{menu_id}` - 메뉴 삭제
- `PUT /api/menus/{menu_id}/order` - 노출 순서 변경
- `GET /api/customer/stores/{store_id}/menus` - 고객용 메뉴 조회

---

### 1.7 TableComponent
**목적**: 테이블 및 세션 관리
**책임**:
- 테이블 초기 설정 (번호, 비밀번호)
- 테이블 세션 라이프사이클 관리
- 테이블 이용 완료 처리
- 세션 시작/종료 관리

**인터페이스**:
- `POST /api/stores/{store_id}/tables` - 테이블 등록/설정
- `GET /api/stores/{store_id}/tables` - 테이블 목록 조회
- `POST /api/tables/{table_id}/complete` - 이용 완료 처리
- `GET /api/tables/{table_id}/session` - 현재 세션 조회

---

### 1.8 OrderComponent
**목적**: 주문 처리 및 관리
**책임**:
- 주문 생성 (고객)
- 주문 상태 변경 (관리자: 대기중→준비중→완료)
- 주문 삭제 (관리자 직권)
- 주문 내역 조회 (현재 세션 / 과거 이력)
- 주문 이력 관리 (세션 종료 시 이동)
- 테이블별 총 주문액 계산

**인터페이스**:
- `POST /api/orders` - 주문 생성
- `GET /api/tables/{table_id}/orders` - 테이블 현재 세션 주문 조회
- `GET /api/stores/{store_id}/orders` - 매장 전체 주문 조회 (관리자)
- `PATCH /api/orders/{order_id}/status` - 주문 상태 변경
- `DELETE /api/orders/{order_id}` - 주문 삭제
- `GET /api/tables/{table_id}/order-history` - 과거 주문 내역 조회

---

### 1.9 SSEComponent
**목적**: 실시간 이벤트 스트리밍
**책임**:
- 관리자용 주문 실시간 알림 (신규 주문, 상태 변경)
- 고객용 주문 상태 실시간 업데이트
- SSE 연결 관리 (매장별, 테이블별)

**인터페이스**:
- `GET /api/sse/admin/stores/{store_id}/orders` - 관리자 주문 SSE 스트림
- `GET /api/sse/customer/tables/{table_id}/orders` - 고객 주문 상태 SSE 스트림

---

### 1.10 FileUploadComponent
**목적**: 파일 업로드 공통 처리
**책임**:
- 이미지 파일 업로드 및 저장
- 파일 형식 검증 (JPG, PNG)
- 파일 경로 관리
- 파일 삭제

**인터페이스**:
- 내부 서비스 (다른 컴포넌트에서 호출)
- `POST /api/upload` - 파일 업로드 (공통)

---

## 2. Frontend 컴포넌트

### 2.1 Customer Frontend (Vue.js)

| 컴포넌트 | 목적 |
|---|---|
| **AdScreen** | 광고 화면 (랜딩 페이지, 자동 슬라이드) |
| **MenuBrowser** | 메뉴 탐색 (카테고리별, 카드 레이아웃) |
| **CartManager** | 장바구니 관리 (로컬 저장, 수량 조절) |
| **PaymentSelector** | 결제 방식 선택 팝업 (더치페이/단독) |
| **LadderGame** | 사다리 타기 미니게임 (애니메이션, 효과음) |
| **OrderConfirm** | 주문 확정 화면 |
| **OrderHistory** | 주문 내역 조회 (SSE 실시간 업데이트) |
| **TableAuth** | 테이블 초기 설정 / 자동 로그인 |

### 2.2 Admin Frontend (Vue.js)

| 컴포넌트 | 목적 |
|---|---|
| **AdminLogin** | 관리자 로그인 (슈퍼/매장) |
| **StoreDashboard** | 매장 관리 대시보드 (슈퍼 관리자) |
| **StoreManager** | 매장 CRUD (슈퍼 관리자) |
| **AdminManager** | 관리자 계정 관리 (슈퍼 관리자) |
| **AdManager** | 광고 이미지 관리 (슈퍼 관리자) |
| **MenuManager** | 메뉴 CRUD + 이미지 업로드 + 순서 조정 |
| **OrderMonitor** | 실시간 주문 모니터링 (SSE, 그리드 레이아웃) |
| **OrderDetail** | 주문 상세 보기 + 상태 변경 |
| **TableManager** | 테이블 관리 (설정, 이용 완료, 과거 내역) |

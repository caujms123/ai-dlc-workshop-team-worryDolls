# Unit 1: Frontend 컴포넌트 설계 - Admin UI (인증 + 매장 + 관리자 + 광고)

---

## 1. 컴포넌트 계층 구조

```
App.vue
+-- router-view
    +-- LoginView.vue (공개)
    +-- AdminLayout.vue (인증 필요)
        +-- Sidebar.vue
        +-- HeaderBar.vue
        +-- router-view
            +-- StoreDashboard.vue (슈퍼 관리자)
            |   +-- StoreList.vue
            |   +-- StoreForm.vue (등록/수정 모달)
            +-- AdminManagerView.vue (슈퍼 관리자)
            |   +-- AdminList.vue
            |   +-- AdminForm.vue (생성/수정 모달)
            +-- AdManagerView.vue (슈퍼 관리자)
                +-- AdList.vue
                +-- AdUploadForm.vue
```

---

## 2. 컴포넌트 상세

### 2.1 LoginView.vue
**목적**: 슈퍼 관리자 / 매장 관리자 로그인

**State**:
- `loginType`: 'super' | 'store' (탭 전환)
- `storeCode`: string (매장 관리자만)
- `username`: string
- `password`: string
- `isLoading`: boolean
- `errorMessage`: string

**사용자 상호작용**:
- 로그인 유형 탭 전환 (슈퍼 관리자 / 매장 관리자)
- 폼 입력 및 제출
- 에러 메시지 표시

**API 연동**:
- `POST /api/auth/admin/login` → 토큰 저장 (localStorage)
- 성공 시 대시보드로 라우팅

**폼 검증**:
- storeCode: 필수 (매장 관리자), 3~30자
- username: 필수, 2~50자
- password: 필수, 8자 이상

---

### 2.2 StoreDashboard.vue
**목적**: 매장 목록 조회 및 관리

**State**:
- `stores`: Store[]
- `isLoading`: boolean
- `showForm`: boolean
- `editingStore`: Store | null

**사용자 상호작용**:
- 매장 목록 테이블 표시
- "매장 등록" 버튼 → StoreForm 모달
- 매장 행 클릭 → StoreForm 수정 모달

**API 연동**:
- `GET /api/stores` → 매장 목록
- `POST /api/stores` → 매장 등록
- `PUT /api/stores/{id}` → 매장 수정

---

### 2.3 StoreForm.vue
**목적**: 매장 등록/수정 폼 (모달)

**Props**:
- `store`: Store | null (수정 시 기존 데이터)
- `isEdit`: boolean

**Emits**:
- `save`: 저장 완료
- `close`: 모달 닫기

**폼 검증**:
- store_code: 필수, 영문소문자+숫자+하이픈, 3~30자 (등록 시만)
- name: 필수, 2~100자
- address: 선택, 최대 255자
- phone: 선택, 전화번호 형식

---

### 2.4 AdminManagerView.vue
**목적**: 매장별 관리자 계정 관리

**State**:
- `selectedStoreId`: number
- `admins`: Admin[]
- `isLoading`: boolean
- `showForm`: boolean

**사용자 상호작용**:
- 매장 선택 드롭다운
- 관리자 목록 테이블
- "관리자 생성" 버튼 → AdminForm 모달
- 활성/비활성 토글 버튼

**API 연동**:
- `GET /api/stores` → 매장 목록 (드롭다운)
- `GET /api/stores/{id}/admins` → 관리자 목록
- `POST /api/stores/{id}/admins` → 관리자 생성
- `PATCH /api/admins/{id}/status` → 활성/비활성

---

### 2.5 AdminForm.vue
**목적**: 관리자 계정 생성 폼 (모달)

**Props**:
- `storeId`: number

**Emits**:
- `save`: 저장 완료
- `close`: 모달 닫기

**폼 검증**:
- username: 필수, 2~50자
- password: 필수, 8자 이상

---

### 2.6 AdManagerView.vue
**목적**: 매장별 광고 이미지 관리

**State**:
- `selectedStoreId`: number
- `advertisements`: Advertisement[]
- `isLoading`: boolean

**사용자 상호작용**:
- 매장 선택 드롭다운
- 광고 이미지 그리드/리스트 표시
- 이미지 업로드 버튼
- 순서 변경 (드래그 또는 화살표 버튼)
- 활성/비활성 토글
- 삭제 버튼 (확인 팝업)

**API 연동**:
- `GET /api/stores/{id}/advertisements` → 광고 목록
- `POST /api/stores/{id}/advertisements` → 이미지 업로드 (multipart/form-data)
- `PUT /api/advertisements/{id}/order` → 순서 변경
- `PATCH /api/advertisements/{id}/status` → 활성/비활성
- `DELETE /api/advertisements/{id}` → 삭제

---

### 2.7 Sidebar.vue
**목적**: 좌측 네비게이션 메뉴

**Props**:
- `userRole`: 'SUPER_ADMIN' | 'STORE_ADMIN'

**메뉴 항목**:
- 슈퍼 관리자: 매장 관리, 관리자 관리, 광고 관리
- 매장 관리자: 주문 모니터링, 메뉴 관리, 테이블 관리
- 공통: 로그아웃

---

### 2.8 HeaderBar.vue
**목적**: 상단 헤더 (사용자 정보, 로그아웃)

**State**:
- `currentUser`: UserInfo

**사용자 상호작용**:
- 사용자명/역할 표시
- 로그아웃 버튼

---

## 3. 상태 관리 (Pinia Store)

### authStore
```
state:
  token: string | null
  user: { id, role, store_id, username } | null
  isAuthenticated: boolean

actions:
  login(credentials) → API 호출, 토큰 저장
  logout() → 토큰 삭제, 상태 초기화
  checkAuth() → 토큰 유효성 확인

getters:
  isSuperAdmin: boolean
  isStoreAdmin: boolean
  currentStoreId: number | null
```

---

## 4. 라우터 설정

| 경로 | 컴포넌트 | 인증 | 역할 |
|---|---|---|---|
| `/login` | LoginView | 불필요 | - |
| `/stores` | StoreDashboard | 필요 | SUPER_ADMIN |
| `/admins` | AdminManagerView | 필요 | SUPER_ADMIN |
| `/advertisements` | AdManagerView | 필요 | SUPER_ADMIN |
| `/orders` | OrderMonitor (Unit 3) | 필요 | STORE_ADMIN |
| `/menus` | MenuManager (Unit 2) | 필요 | STORE_ADMIN |
| `/tables` | TableManager (Unit 4) | 필요 | STORE_ADMIN |

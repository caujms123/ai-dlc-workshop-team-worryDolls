# Unit 4: Frontend 컴포넌트 설계 - 고객 UI + 테이블 관리

---

## 1. Customer Frontend

### 1.1 AdScreen.vue
**목적**: 광고 화면 (랜딩 페이지)

**State**:
- `advertisements`: Advertisement[]
- `currentIndex`: number
- `slideTimer`: Timer
- `inactivityTimer`: Timer

**동작**:
- 마운트 시 활성 광고 목록 API 호출
- 5초 간격 자동 슬라이드 (currentIndex 순환)
- 화면 터치 → router.push('/menu')
- 2분 비활성 타이머 (메뉴 화면에서 복귀용, App 레벨에서 관리)

**API**: `GET /api/customer/stores/{store_id}/advertisements`

---

### 1.2 TableAuthView.vue
**목적**: 테이블 초기 설정 화면

**State**:
- `storeCode`: string
- `tableNumber`: number
- `password`: string
- `isLoading`: boolean
- `errorMessage`: string

**동작**:
- 자동 로그인 실패 시 표시
- 폼 제출 → 로그인 API → 토큰 + 자격 증명 localStorage 저장
- 성공 시 광고 화면으로 이동

**API**: `POST /api/auth/table/login`

---

### 1.3 CartView.vue
**목적**: 장바구니 관리 화면

**State** (Pinia cartStore):
- `items`: CartItem[] (localStorage 동기화)
- `totalAmount`: computed

**사용자 상호작용**:
- 각 항목: 메뉴명, 단가, 수량 (+/- 버튼), 소계
- 수량 0 시 자동 제거
- "장바구니 비우기" 버튼
- 총 금액 표시
- "주문하기" 버튼 → PaymentSelector 팝업

---

### 1.4 PaymentSelector.vue (팝업)
**목적**: 결제 방식 선택

**Props**: `totalAmount: number`
**Emits**: `select(paymentType)`, `close`

**State**:
- `showLadderGame`: boolean

**레이아웃**:
- 제목: "결제 방식 선택"
- 오른쪽 상단: 사다리 타기 버튼 (🎲 아이콘)
- 본문: 두 개의 큰 버튼
  - "더치페이 (1/N)" → emit('select', 'DUTCH_PAY')
  - "단독 계산" → emit('select', 'SINGLE_PAY')

---

### 1.5 LadderGame.vue
**목적**: 사다리 타기 미니게임

**State**:
- `phase`: 'select_players' | 'ready' | 'playing' | 'result'
- `playerCount`: number (2~10)
- `ladder`: LadderData (세로줄, 가로줄, 꽝 위치)
- `animationProgress`: number[]
- `loser`: number | null
- `resultTimer`: Timer

**컴포넌트 구조**:
```
LadderGame.vue
+-- PlayerCountSelector.vue (인원 선택)
+-- LadderCanvas.vue (사다리 렌더링 + 애니메이션)
+-- LadderResult.vue (결과 표시)
```

**사다리 생성 알고리즘**:
1. 세로줄 수 = playerCount
2. 구간 수 = playerCount * 2 (충분한 복잡도)
3. 각 구간에서 인접한 두 세로줄 사이에 가로줄 랜덤 배치 (0~2개)
4. 꽝 위치: 하단 랜덤 1개

**애니메이션**:
- CSS transition 또는 requestAnimationFrame
- 각 참가자가 위에서 아래로 이동
- 가로줄 만나면 좌/우 이동
- 이동 속도: 약 2~3초 전체

**효과음**:
- 시작: 출발 효과음
- 이동 중: 틱틱 효과음
- 결과: 꽝 효과음 (팡파레 또는 코믹 효과)

**결과 연출**:
- 꽝 참가자 칸: 빨간색 배경 + 크기 확대 (scale 1.2)
- "꽝!" 텍스트 오버레이
- 5초 카운트다운 표시
- 5초 후 emit('complete') → PaymentSelector로 복귀

---

## 2. Admin Frontend

### 2.1 TableManagerView.vue
**목적**: 테이블 관리 화면

**State**:
- `tables`: TableInfo[]
- `showForm`: boolean
- `editingTable`: TableInfo | null

**사용자 상호작용**:
- 테이블 목록 (번호, 상태, 현재 세션 여부)
- "테이블 추가" 버튼 → TableForm 모달
- 각 테이블: 설정 수정 버튼

**API 연동**:
- `GET /api/stores/{id}/tables`
- `POST /api/stores/{id}/tables`

### TableForm.vue (모달)
**Props**: `table: TableInfo | null`, `storeId: number`
**Emits**: `save`, `close`

**폼 필드**:
- 테이블 번호 (필수, 양수)
- 비밀번호 (필수, 4자 이상)

---

## 3. 상태 관리 (Pinia Store)

### cartStore (Customer)
```
state:
  items: CartItem[]

actions:
  addItem(menu) → 추가 또는 수량 증가
  removeItem(menuId) → 항목 제거
  updateQuantity(menuId, quantity) → 수량 변경
  clearCart() → 전체 비우기
  loadFromStorage() → localStorage에서 로드
  saveToStorage() → localStorage에 저장

getters:
  totalAmount: number
  itemCount: number
  isEmpty: boolean
```

### tableAuthStore (Customer)
```
state:
  token: string | null
  storeId: number | null
  tableId: number | null
  tableNumber: number | null

actions:
  login(credentials) → API 호출, 토큰 저장
  autoLogin() → 저장된 토큰으로 자동 로그인
  logout() → 토큰 삭제

getters:
  isAuthenticated: boolean
```

---

## 4. Customer 라우터

| 경로 | 컴포넌트 | 인증 | 설명 |
|---|---|---|---|
| `/` | AdScreen | 필요 | 광고 화면 (기본) |
| `/setup` | TableAuthView | 불필요 | 초기 설정 |
| `/menu` | MenuView (Unit 2) | 필요 | 메뉴 탐색 |
| `/cart` | CartView | 필요 | 장바구니 |
| `/order/confirm` | OrderConfirmView (Unit 3) | 필요 | 주문 확정 |
| `/orders` | OrderHistoryView (Unit 3) | 필요 | 주문 내역 |

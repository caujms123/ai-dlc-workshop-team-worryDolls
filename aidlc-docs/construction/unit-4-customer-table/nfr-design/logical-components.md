# Unit 4: Logical Components - 고객 UI + 테이블 관리

---

## 1. Customer App 전체 구조

```
App.vue
  |
  +-- InactivityWatcher (비활성 감지, 2분)
  |
  +-- router-view
      |
      +-- / (AdScreen) ← 기본 화면
      |     +-- ImageSlider (5초 자동)
      |     +-- TouchOverlay (터치 감지)
      |
      +-- /setup (TableAuthView)
      |     +-- LoginForm
      |
      +-- /menu (MenuView) ← Unit 2
      |     +-- CategoryTabs
      |     +-- MenuGrid
      |     +-- CartBadge (장바구니 아이콘)
      |
      +-- /cart (CartView)
      |     +-- CartItemList
      |     +-- CartSummary
      |     +-- PaymentSelector (팝업)
      |     |     +-- LadderGameButton
      |     |     +-- DutchPayButton
      |     |     +-- SinglePayButton
      |     +-- LadderGame (팝업)
      |           +-- PlayerCountSelector
      |           +-- LadderCanvas
      |           +-- LadderResult
      |
      +-- /order/confirm (OrderConfirmView) ← Unit 3
      +-- /orders (OrderHistoryView) ← Unit 3
```

---

## 2. 사다리 타기 컴포넌트 구조

```
LadderGame.vue
  |
  +-- Phase: select_players
  |     +-- PlayerCountSelector.vue
  |           +-- 숫자 버튼 (2~10)
  |           +-- "시작" 버튼
  |
  +-- Phase: playing
  |     +-- LadderCanvas.vue
  |           +-- Canvas/SVG 렌더링
  |           +-- 이동 애니메이션
  |           +-- SoundManager (효과음)
  |
  +-- Phase: result
        +-- LadderResult.vue
              +-- 꽝 강조 (빨간색, scale 1.2)
              +-- "꽝!" 텍스트
              +-- 5초 카운트다운
              +-- 자동 복귀
```

---

## 3. 테이블 관리 (Admin) 구조

```
TableManagerView.vue
  |
  +-- TableList
  |     +-- 테이블 번호, 상태, 세션 여부
  |     +-- 설정 수정 버튼
  |
  +-- TableForm (모달)
        +-- 테이블 번호 입력
        +-- 비밀번호 입력
```

---

## 4. 네비게이션 바 (Customer)

```
BottomNav.vue (하단 고정)
  |
  +-- 메뉴 (MenuView)
  +-- 장바구니 (CartView) + 배지 (수량)
  +-- 주문내역 (OrderHistoryView)
```

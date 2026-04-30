# Unit 2: Frontend 컴포넌트 설계 - 메뉴 관리

---

## 1. Admin Frontend - MenuManager

### MenuManagerView.vue
**목적**: 메뉴 CRUD 관리 화면

**State**:
- `categories`: Category[]
- `menus`: Menu[] (선택된 카테고리의 메뉴)
- `selectedCategoryId`: number | null
- `showMenuForm`: boolean
- `showCategoryForm`: boolean
- `editingMenu`: Menu | null

**사용자 상호작용**:
- 좌측: 카테고리 목록 (추가/수정/삭제 버튼)
- 우측: 선택된 카테고리의 메뉴 목록
- 메뉴 카드에 수정/삭제 버튼
- 순서 변경 (위/아래 화살표)
- "메뉴 등록" 버튼 → MenuForm 모달

**API 연동**:
- `GET /api/stores/{id}/categories`
- `GET /api/stores/{id}/menus?category_id={id}`
- `DELETE /api/menus/{id}`
- `PUT /api/menus/{id}/order`

### MenuForm.vue (모달)
**Props**: `menu: Menu | null`, `categories: Category[]`, `storeId: number`
**Emits**: `save`, `close`

**폼 필드**:
- 메뉴명 (필수, 2~100자)
- 가격 (필수, 0 이상)
- 설명 (선택)
- 카테고리 선택 (필수)
- 이미지 업로드 (선택, 미리보기 표시)

### CategoryForm.vue (모달)
**Props**: `category: Category | null`, `storeId: number`
**Emits**: `save`, `close`

**폼 필드**:
- 카테고리명 (필수, 2~50자)

---

## 2. Customer Frontend - MenuBrowser

### MenuView.vue
**목적**: 고객용 메뉴 탐색 화면

**State**:
- `categoriesWithMenus`: CategoryWithMenus[]
- `selectedCategoryId`: number | null
- `selectedMenu`: Menu | null (상세 보기)
- `isLoading`: boolean

**사용자 상호작용**:
- 상단: 카테고리 탭 (가로 스크롤)
- 본문: 메뉴 카드 그리드 (2열)
- 카드 터치 → 메뉴 상세 팝업
- 상세 팝업에서 "장바구니 추가" 버튼

**API 연동**:
- `GET /api/customer/stores/{store_id}/menus`

### MenuCard.vue
**Props**: `menu: Menu`
**Emits**: `select`, `addToCart`

**표시 정보**: 이미지, 메뉴명, 가격
**터치 타겟**: 최소 44x44px

### MenuDetail.vue (팝업)
**Props**: `menu: Menu`
**Emits**: `addToCart`, `close`

**표시 정보**: 이미지 (크게), 메뉴명, 가격, 설명
**버튼**: "장바구니에 추가", "닫기"

# Unit 2: Logical Components - 메뉴 관리

---

## 1. 메뉴 관리 컴포넌트 구조

```
+---------------------------+
| MenuRouter                |
| - Admin: CRUD endpoints   |
| - Customer: 조회 endpoint |
+---------------------------+
            |
            v
+---------------------------+
| MenuService               |
| - create_menu()           |
| - update_menu()           |
| - delete_menu()           |
| - get_customer_menus()    |
+---------------------------+
     |              |
     v              v
+-----------+  +------------------+
| MenuRepo  |  | FileUploadSvc    |
|           |  | (Unit 1 제공)    |
+-----------+  +------------------+

+---------------------------+
| CategoryRouter            |
+---------------------------+
            |
            v
+---------------------------+
| CategoryService           |
+---------------------------+
            |
            v
+---------------------------+
| CategoryRepository        |
+---------------------------+
```

---

## 2. Customer Frontend 메뉴 탐색 구조

```
MenuView.vue
  |
  +-- CategoryTabs (상단 카테고리 탭)
  |     |
  |     +-- scrollIntoView (카테고리 빠른 이동)
  |
  +-- MenuGrid (메뉴 카드 그리드, 2열)
  |     |
  |     +-- MenuCard (개별 메뉴 카드)
  |           |
  |           +-- lazy-loaded image
  |
  +-- MenuDetail (팝업, 선택 시)
        |
        +-- "장바구니 추가" 버튼 → cartStore.addItem()
```

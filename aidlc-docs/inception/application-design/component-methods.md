# 테이블오더 서비스 - 컴포넌트 메서드 정의

> **Note**: 상세 비즈니스 로직은 Functional Design (CONSTRUCTION) 단계에서 정의됩니다.
> 여기서는 메서드 시그니처와 고수준 목적만 정의합니다.

---

## 1. AuthService

| 메서드 | 입력 | 출력 | 목적 |
|---|---|---|---|
| `login_admin(store_code, username, password)` | str, str, str | TokenResponse | 관리자 로그인, JWT 발급 |
| `login_super_admin(username, password)` | str, str | TokenResponse | 슈퍼 관리자 로그인 |
| `login_table(store_code, table_number, password)` | str, int, str | TokenResponse | 테이블 태블릿 로그인 |
| `auto_login_table(stored_token)` | str | TokenResponse | 저장된 토큰으로 자동 로그인 |
| `verify_token(token)` | str | UserInfo | JWT 토큰 검증 |
| `logout(token)` | str | None | 로그아웃 처리 |
| `check_login_attempts(identifier)` | str | bool | 로그인 시도 제한 확인 |
| `hash_password(password)` | str | str | bcrypt 해싱 |
| `verify_password(plain, hashed)` | str, str | bool | 비밀번호 검증 |

---

## 2. StoreService

| 메서드 | 입력 | 출력 | 목적 |
|---|---|---|---|
| `create_store(store_data)` | StoreCreate | Store | 매장 등록 |
| `get_stores()` | None | List[Store] | 매장 목록 조회 |
| `get_store(store_id)` | int | Store | 매장 상세 조회 |
| `update_store(store_id, store_data)` | int, StoreUpdate | Store | 매장 수정 |
| `validate_store_code(code)` | str | bool | 매장 식별자 고유성 검증 |

---

## 3. AdminService

| 메서드 | 입력 | 출력 | 목적 |
|---|---|---|---|
| `create_admin(store_id, admin_data)` | int, AdminCreate | Admin | 관리자 생성 |
| `get_admins(store_id)` | int | List[Admin] | 매장별 관리자 목록 |
| `update_admin(admin_id, admin_data)` | int, AdminUpdate | Admin | 관리자 수정 |
| `toggle_admin_status(admin_id)` | int | Admin | 활성/비활성 전환 |
| `validate_username(store_id, username)` | int, str | bool | 사용자명 중복 검증 |

---

## 4. AdvertisementService

| 메서드 | 입력 | 출력 | 목적 |
|---|---|---|---|
| `upload_ad(store_id, image_file)` | int, UploadFile | Advertisement | 광고 이미지 업로드 |
| `get_ads(store_id)` | int | List[Advertisement] | 광고 목록 조회 (관리자) |
| `get_active_ads(store_id)` | int | List[Advertisement] | 활성 광고 조회 (고객) |
| `delete_ad(ad_id)` | int | None | 광고 삭제 |
| `update_ad_order(ad_id, new_order)` | int, int | Advertisement | 노출 순서 변경 |
| `toggle_ad_status(ad_id)` | int | Advertisement | 활성/비활성 전환 |

---

## 5. CategoryService

| 메서드 | 입력 | 출력 | 목적 |
|---|---|---|---|
| `create_category(store_id, category_data)` | int, CategoryCreate | Category | 카테고리 등록 |
| `get_categories(store_id)` | int | List[Category] | 카테고리 목록 조회 |
| `update_category(category_id, data)` | int, CategoryUpdate | Category | 카테고리 수정 |
| `delete_category(category_id)` | int | None | 카테고리 삭제 |

---

## 6. MenuService

| 메서드 | 입력 | 출력 | 목적 |
|---|---|---|---|
| `create_menu(store_id, menu_data, image)` | int, MenuCreate, UploadFile | Menu | 메뉴 등록 |
| `get_menus(store_id, category_id?)` | int, int? | List[Menu] | 메뉴 목록 조회 |
| `get_menu(menu_id)` | int | Menu | 메뉴 상세 조회 |
| `update_menu(menu_id, menu_data, image?)` | int, MenuUpdate, UploadFile? | Menu | 메뉴 수정 |
| `delete_menu(menu_id)` | int | None | 메뉴 삭제 |
| `update_menu_order(menu_id, new_order)` | int, int | Menu | 노출 순서 변경 |
| `get_customer_menus(store_id)` | int | List[MenuWithCategory] | 고객용 메뉴 조회 |

---

## 7. TableService

| 메서드 | 입력 | 출력 | 목적 |
|---|---|---|---|
| `create_table(store_id, table_data)` | int, TableCreate | TableInfo | 테이블 등록/설정 |
| `get_tables(store_id)` | int | List[TableInfo] | 테이블 목록 조회 |
| `get_current_session(table_id)` | int | TableSession | 현재 세션 조회 |
| `start_session(table_id)` | int | TableSession | 세션 시작 (첫 주문 시) |
| `complete_table(table_id)` | int | None | 이용 완료 처리 |

---

## 8. OrderService

| 메서드 | 입력 | 출력 | 목적 |
|---|---|---|---|
| `create_order(order_data)` | OrderCreate | Order | 주문 생성 |
| `get_table_orders(table_id, session_id)` | int, int | List[Order] | 테이블 현재 세션 주문 |
| `get_store_orders(store_id)` | int | List[OrderSummary] | 매장 전체 주문 (관리자) |
| `update_order_status(order_id, status)` | int, OrderStatus | Order | 주문 상태 변경 |
| `delete_order(order_id)` | int | None | 주문 삭제 |
| `get_order_history(table_id, date?)` | int, date? | List[OrderHistory] | 과거 주문 내역 |
| `move_to_history(session_id)` | int | None | 세션 주문을 이력으로 이동 |
| `get_table_total(table_id, session_id)` | int, int | int | 테이블 총 주문액 |

---

## 9. SSEService

| 메서드 | 입력 | 출력 | 목적 |
|---|---|---|---|
| `subscribe_admin(store_id)` | int | EventStream | 관리자 주문 SSE 구독 |
| `subscribe_customer(table_id)` | int | EventStream | 고객 주문 상태 SSE 구독 |
| `publish_order_event(store_id, event)` | int, OrderEvent | None | 주문 이벤트 발행 |
| `publish_status_event(table_id, event)` | int, StatusEvent | None | 상태 변경 이벤트 발행 |

---

## 10. FileUploadService

| 메서드 | 입력 | 출력 | 목적 |
|---|---|---|---|
| `upload_image(file, directory)` | UploadFile, str | str | 이미지 업로드, URL 반환 |
| `delete_image(file_path)` | str | None | 이미지 파일 삭제 |
| `validate_image(file)` | UploadFile | bool | 이미지 형식 검증 (JPG, PNG) |

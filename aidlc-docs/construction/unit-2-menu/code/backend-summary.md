# Unit 2: Backend Code Summary - 메뉴 관리

## 생성된 파일

### Database Models
| 파일 | 설명 |
|---|---|
| `backend/app/models/category.py` | Category 모델 (SQLAlchemy) |
| `backend/app/models/menu.py` | Menu 모델 (SQLAlchemy) |

### Pydantic Schemas
| 파일 | 설명 |
|---|---|
| `backend/app/schemas/category.py` | CategoryCreate, CategoryUpdate, CategoryResponse |
| `backend/app/schemas/menu.py` | MenuCreate, MenuUpdate, MenuResponse, CustomerMenuResponse |

### Repository Layer
| 파일 | 설명 |
|---|---|
| `backend/app/repositories/category_repo.py` | CategoryRepository (CRUD + reorder) |
| `backend/app/repositories/menu_repo.py` | MenuRepository (CRUD + reorder + customer view) |

### Service Layer
| 파일 | 설명 |
|---|---|
| `backend/app/services/category_service.py` | CategoryService (비즈니스 로직, BR-CAT-01~02) |
| `backend/app/services/menu_service.py` | MenuService (비즈니스 로직, BR-MENU-01~05, FileUpload 연동) |

### API Router Layer
| 파일 | 설명 |
|---|---|
| `backend/app/routers/category.py` | Category REST API (4 endpoints) |
| `backend/app/routers/menu.py` | Menu REST API (7 endpoints, 관리자 + 고객) |

### Tests
| 파일 | 설명 |
|---|---|
| `backend/tests/conftest.py` | 테스트 설정 (SQLite in-memory) |
| `backend/tests/test_category_repo.py` | CategoryRepository 단위 테스트 |
| `backend/tests/test_menu_repo.py` | MenuRepository 단위 테스트 |
| `backend/tests/test_category_service.py` | CategoryService 단위 테스트 |
| `backend/tests/test_menu_service.py` | MenuService 단위 테스트 |
| `backend/tests/test_category_router.py` | Category API 통합 테스트 |
| `backend/tests/test_menu_router.py` | Menu API 통합 테스트 |

## API Endpoints

| Method | Path | 설명 | 권한 |
|---|---|---|---|
| POST | `/api/stores/{store_id}/categories` | 카테고리 등록 | STORE_ADMIN |
| GET | `/api/stores/{store_id}/categories` | 카테고리 목록 | STORE_ADMIN |
| PUT | `/api/categories/{category_id}` | 카테고리 수정 | STORE_ADMIN |
| DELETE | `/api/categories/{category_id}` | 카테고리 삭제 | STORE_ADMIN |
| POST | `/api/stores/{store_id}/menus` | 메뉴 등록 | STORE_ADMIN |
| GET | `/api/stores/{store_id}/menus` | 메뉴 목록 | STORE_ADMIN |
| GET | `/api/menus/{menu_id}` | 메뉴 상세 | STORE_ADMIN |
| PUT | `/api/menus/{menu_id}` | 메뉴 수정 | STORE_ADMIN |
| DELETE | `/api/menus/{menu_id}` | 메뉴 삭제 | STORE_ADMIN |
| PUT | `/api/menus/{menu_id}/order` | 순서 변경 | STORE_ADMIN |
| GET | `/api/customer/stores/{store_id}/menus` | 고객용 메뉴 | TABLE |

## Unit 1 통합 포인트 (TODO)
- AuthMiddleware: 라우터에 `# TODO` 주석으로 표시
- FileUploadService: `SimpleFileUploadService`로 임시 구현, Unit 1 제공 시 교체
- GlobalErrorHandler: `main.py`에 기본 구현 포함

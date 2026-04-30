# Unit Test Execution - Unit 2: 메뉴 관리

## Backend Unit Tests

### 1. 테스트 환경 준비

```bash
cd backend
source venv/bin/activate

# 테스트 의존성 설치
pip install pytest pytest-asyncio httpx aiosqlite
```

> **Note**: 테스트는 SQLite in-memory DB를 사용하므로 MySQL 없이 실행 가능합니다.

### 2. 전체 테스트 실행

```bash
cd backend
python -m pytest tests/ -v
```

### 3. 개별 테스트 파일 실행

```bash
# Repository 테스트
python -m pytest tests/test_category_repo.py -v
python -m pytest tests/test_menu_repo.py -v

# Service 테스트
python -m pytest tests/test_category_service.py -v
python -m pytest tests/test_menu_service.py -v

# API Router 통합 테스트
python -m pytest tests/test_category_router.py -v
python -m pytest tests/test_menu_router.py -v
```

### 4. 예상 테스트 결과

| 테스트 파일 | 테스트 수 | 설명 |
|---|---|---|
| `test_category_repo.py` | 7 | CategoryRepository CRUD + reorder |
| `test_menu_repo.py` | 8 | MenuRepository CRUD + reorder + filter |
| `test_category_service.py` | 6 | CategoryService 비즈니스 로직 + BR-CAT-02 |
| `test_menu_service.py` | 9 | MenuService 비즈니스 로직 + 이미지 + 고객 뷰 |
| `test_category_router.py` | 7 | Category API 엔드포인트 + 검증 |
| `test_menu_router.py` | 9 | Menu API 엔드포인트 + 고객 API |
| **합계** | **~46** | |

### 5. 테스트 커버리지 확인

```bash
pip install pytest-cov
python -m pytest tests/ --cov=backend/app --cov-report=term-missing -v
```

**목표 커버리지**: 80% 이상

---

## Frontend Unit Tests

### Admin Frontend

```bash
cd frontend/admin
npm install
npm run test
```

**테스트 파일**:
| 파일 | 테스트 수 | 설명 |
|---|---|---|
| `CategoryList.spec.js` | 7 | 카테고리 목록 렌더링, 이벤트 |
| `MenuCard.spec.js` | 8 | 메뉴 카드 렌더링, 이벤트 |
| `MenuForm.spec.js` | 5 | 메뉴 폼 렌더링, 검증 |
| `menuStore.spec.js` | 6 | Pinia 스토어 상태 관리 |
| **합계** | **~26** | |

### Customer Frontend

```bash
cd frontend/customer
npm install
npm run test
```

**테스트 파일**:
| 파일 | 테스트 수 | 설명 |
|---|---|---|
| `CategoryTabs.spec.js` | 5 | 카테고리 탭 렌더링, 접근성 |
| `MenuCard.spec.js` | 5 | 메뉴 카드 렌더링, lazy loading |
| `MenuDetail.spec.js` | 6 | 메뉴 상세 팝업, 이벤트 |
| `menuStore.spec.js` | 4 | Pinia 스토어 상태 관리 |
| **합계** | **~20** | |

---

## 전체 테스트 요약

| 레이어 | 테스트 수 | 실행 명령 |
|---|---|---|
| Backend Repository | ~15 | `python -m pytest tests/test_*_repo.py` |
| Backend Service | ~15 | `python -m pytest tests/test_*_service.py` |
| Backend Router | ~16 | `python -m pytest tests/test_*_router.py` |
| Admin Frontend | ~26 | `cd frontend/admin && npm run test` |
| Customer Frontend | ~20 | `cd frontend/customer && npm run test` |
| **전체** | **~92** | |

## 실패 시 대응

1. 테스트 출력에서 실패한 테스트 케이스 확인
2. `FAILED` 표시된 테스트의 에러 메시지 분석
3. 관련 소스 코드 수정
4. 해당 테스트만 재실행하여 확인
5. 전체 테스트 재실행으로 회귀 확인

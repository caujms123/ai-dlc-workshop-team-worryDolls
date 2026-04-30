# Unit 2: Frontend Code Summary - 메뉴 관리

## Admin Frontend (관리자 메뉴 관리)

### 생성된 파일
| 파일 | 설명 |
|---|---|
| `frontend/admin/src/views/MenuView.vue` | 메뉴 관리 메인 화면 |
| `frontend/admin/src/components/menu/CategoryList.vue` | 카테고리 목록 (좌측 패널) |
| `frontend/admin/src/components/menu/CategoryForm.vue` | 카테고리 등록/수정 모달 |
| `frontend/admin/src/components/menu/MenuList.vue` | 메뉴 목록 (우측 패널) |
| `frontend/admin/src/components/menu/MenuCard.vue` | 메뉴 카드 (수정/삭제/순서) |
| `frontend/admin/src/components/menu/MenuForm.vue` | 메뉴 등록/수정 모달 (이미지 포함) |
| `frontend/admin/src/services/menuApi.js` | API 호출 서비스 |
| `frontend/admin/src/stores/menuStore.js` | Pinia 상태 관리 |

### Tests
| 파일 | 설명 |
|---|---|
| `frontend/admin/src/components/menu/__tests__/CategoryList.spec.js` | 카테고리 목록 테스트 |
| `frontend/admin/src/components/menu/__tests__/MenuCard.spec.js` | 메뉴 카드 테스트 |
| `frontend/admin/src/components/menu/__tests__/MenuForm.spec.js` | 메뉴 폼 테스트 |
| `frontend/admin/src/stores/__tests__/menuStore.spec.js` | Pinia 스토어 테스트 |

---

## Customer Frontend (고객 메뉴 탐색)

### 생성된 파일
| 파일 | 설명 |
|---|---|
| `frontend/customer/src/views/MenuView.vue` | 메뉴 탐색 메인 화면 |
| `frontend/customer/src/components/menu/CategoryTabs.vue` | 카테고리 탭 (상단, 가로 스크롤) |
| `frontend/customer/src/components/menu/MenuGrid.vue` | 메뉴 카드 그리드 (2열) |
| `frontend/customer/src/components/menu/MenuCard.vue` | 메뉴 카드 (이미지, 이름, 가격) |
| `frontend/customer/src/components/menu/MenuDetail.vue` | 메뉴 상세 팝업 (장바구니 추가) |
| `frontend/customer/src/services/menuApi.js` | API 호출 서비스 |
| `frontend/customer/src/stores/menuStore.js` | Pinia 상태 관리 |

### Tests
| 파일 | 설명 |
|---|---|
| `frontend/customer/src/components/menu/__tests__/CategoryTabs.spec.js` | 카테고리 탭 테스트 |
| `frontend/customer/src/components/menu/__tests__/MenuCard.spec.js` | 메뉴 카드 테스트 |
| `frontend/customer/src/components/menu/__tests__/MenuDetail.spec.js` | 메뉴 상세 테스트 |
| `frontend/customer/src/stores/__tests__/menuStore.spec.js` | Pinia 스토어 테스트 |

## UX 요구사항 준수
- 터치 타겟: 모든 버튼 최소 44x44px (`min-height: 44px`)
- 이미지 Lazy Loading: `loading="lazy"` 적용
- 카테고리 빠른 이동: 가로 스크롤 탭
- 메뉴 카드 그리드: 2열 레이아웃
- `data-testid` 속성: 모든 인터랙티브 요소에 적용

## Unit 4 통합 포인트 (TODO)
- 장바구니 추가: `handleAddToCart()` → `cartStore.addItem()` 연동 필요
- storeId: 테이블 인증 컨텍스트에서 가져오도록 변경 필요

# Integration Test Instructions - Unit 2: 메뉴 관리

## Purpose
Unit 2 (메뉴 관리)와 다른 Unit 간의 상호작용을 테스트합니다.

---

## Unit 간 통합 포인트

### Unit 1 → Unit 2: 인증 + 파일 업로드
| 통합 포인트 | 설명 |
|---|---|
| AuthMiddleware | JWT 토큰 검증, STORE_ADMIN 역할 확인 |
| FileUploadService | 메뉴 이미지 업로드/삭제 |
| Store 모델 | Category, Menu의 FK 참조 |

### Unit 2 → Unit 3: 메뉴 → 주문
| 통합 포인트 | 설명 |
|---|---|
| Menu 데이터 | 주문 생성 시 메뉴 유효성 검증 |
| 가격 정보 | 주문 금액 계산에 메뉴 가격 사용 |

### Unit 2 → Unit 4: 메뉴 → 고객 UI
| 통합 포인트 | 설명 |
|---|---|
| 고객 메뉴 API | 장바구니에 메뉴 추가 시 메뉴 데이터 사용 |
| 이미지 경로 | 고객 화면에서 메뉴 이미지 표시 |

---

## Integration Test Scenarios

### Scenario 1: 인증된 관리자의 메뉴 CRUD

**전제 조건**: Unit 1 AuthService가 동작 중

```
1. POST /api/auth/admin/login → JWT 토큰 획득
2. POST /api/stores/{store_id}/categories (Authorization: Bearer {token})
   → 201 Created (인증 성공)
3. POST /api/stores/{store_id}/menus (Authorization: Bearer {token}, multipart)
   → 201 Created (이미지 업로드 포함)
4. 토큰 없이 POST /api/stores/{store_id}/menus
   → 401 Unauthorized
5. 다른 매장 관리자 토큰으로 접근
   → 403 Forbidden
```

### Scenario 2: 메뉴 이미지 업로드 통합

**전제 조건**: Unit 1 FileUploadService가 동작 중

```
1. 메뉴 등록 시 이미지 파일 첨부
   → 이미지가 uploads/menus/{store_id}/ 에 저장됨
2. 메뉴 수정 시 새 이미지 첨부
   → 기존 이미지 삭제, 새 이미지 저장
3. 메뉴 삭제
   → 이미지 파일도 함께 삭제됨
4. GET /api/uploads/{image_path}
   → 이미지 파일 정상 서빙
```

### Scenario 3: 고객 메뉴 조회 → 장바구니 추가

**전제 조건**: Unit 4 CartManager가 동작 중

```
1. GET /api/customer/stores/{store_id}/menus
   → 카테고리별 그룹화된 메뉴 목록 반환
2. 고객 UI에서 메뉴 카드 터치 → 상세 팝업
3. "장바구니에 추가" 클릭
   → cartStore.addItem(menu) 호출
4. 장바구니에 메뉴 정보(id, name, price) 저장 확인
```

### Scenario 4: 메뉴 변경 → 주문 영향

```
1. 관리자가 메뉴 가격 변경 (9000 → 12000)
2. 이미 장바구니에 담긴 메뉴의 가격은 변경되지 않음 (로컬 저장)
3. 새로 장바구니에 추가하면 변경된 가격 적용
4. 관리자가 메뉴를 is_available=false로 변경
5. 고객 메뉴 조회 시 해당 메뉴 미표시
```

---

## 수동 통합 테스트 절차

### 환경 준비

```bash
# 1. Backend 서버 실행
cd backend
source venv/bin/activate
uvicorn backend.app.main:app --reload --port 8000

# 2. Admin Frontend 실행
cd frontend/admin
npm run dev

# 3. Customer Frontend 실행
cd frontend/customer
npm run dev
```

### 테스트 실행

1. **Admin Frontend** (`http://localhost:5174/menu`)
   - 카테고리 등록 → 목록에 표시 확인
   - 메뉴 등록 (이미지 포함) → 목록에 표시 확인
   - 메뉴 수정 → 변경 사항 반영 확인
   - 메뉴 순서 변경 → 순서 반영 확인
   - 메뉴 삭제 → 목록에서 제거 확인
   - 카테고리 삭제 (메뉴 있을 때) → 409 에러 확인

2. **Customer Frontend** (`http://localhost:5173/menu`)
   - 카테고리 탭 표시 확인
   - 메뉴 카드 그리드 (2열) 표시 확인
   - 메뉴 카드 터치 → 상세 팝업 확인
   - 이미지 lazy loading 확인
   - 품절 메뉴 미표시 확인

3. **API 직접 테스트** (`http://localhost:8000/docs`)
   - Swagger UI에서 각 엔드포인트 테스트
   - 입력 검증 에러 확인 (422)
   - 존재하지 않는 리소스 접근 (404)

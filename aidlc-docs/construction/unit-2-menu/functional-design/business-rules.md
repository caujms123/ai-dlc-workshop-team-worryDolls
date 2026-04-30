# Unit 2: 비즈니스 규칙 - 메뉴 관리

---

## 1. 카테고리 규칙

### BR-CAT-01: 카테고리 생성
- 카테고리명 필수 (2~50자)
- 동일 매장 내 카테고리명 중복 허용 (순서로 구분)
- display_order는 자동 할당 (마지막+1)

### BR-CAT-02: 카테고리 삭제
- 해당 카테고리에 메뉴가 있으면 삭제 불가 (409 Conflict)
- 삭제 후 나머지 카테고리 display_order 재정렬

---

## 2. 메뉴 규칙

### BR-MENU-01: 메뉴 등록 필수 필드
- name: 필수, 2~100자
- price: 필수, 0 이상 정수
- category_id: 필수, 해당 매장의 카테고리여야 함
- description: 선택
- image: 선택 (JPG, PNG, 최대 5MB)

### BR-MENU-02: 메뉴 가격 검증
- 0 이상의 정수만 허용
- 최대 가격: 10,000,000원

### BR-MENU-03: 메뉴 이미지
- 이미지 업로드 시 FileUploadService 사용 (Unit 1 제공)
- 저장 경로: `uploads/menus/{store_id}/{uuid}.{ext}`
- 메뉴 수정 시 새 이미지 업로드하면 기존 이미지 삭제
- 메뉴 삭제 시 이미지 파일도 삭제

### BR-MENU-04: 메뉴 노출 순서
- 카테고리 내에서 display_order로 정렬
- 순서 변경 시 해당 카테고리 내 다른 메뉴의 순서도 재정렬

### BR-MENU-05: 고객용 메뉴 조회
- is_available=true인 메뉴만 표시
- 카테고리별로 그룹화하여 반환
- 카테고리 display_order → 메뉴 display_order 순으로 정렬
- 해당 매장의 메뉴만 반환

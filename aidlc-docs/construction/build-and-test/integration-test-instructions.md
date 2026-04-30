# Integration Test Instructions - Unit 4

## 목적
Unit 4의 컴포넌트 간 통합 및 다른 Unit과의 연동을 검증합니다.

---

## 사전 조건
- MySQL 실행 중, table_order DB 생성됨
- Backend 서버 실행 중 (port 8000)
- Unit 1 (Auth) 코드가 통합된 상태

---

## 시나리오 1: 테이블 등록 → 로그인 → 광고 화면

### 설명
매장 관리자가 테이블을 등록하고, 고객이 해당 테이블로 로그인하여 광고 화면을 확인

### 테스트 단계
1. **매장 관리자 로그인** (Unit 1 API)
   ```bash
   curl -X POST http://localhost:8000/api/auth/admin/login \
     -H "Content-Type: application/json" \
     -d '{"store_code":"store1","username":"admin","password":"password"}'
   ```

2. **테이블 등록**
   ```bash
   curl -X POST http://localhost:8000/api/stores/1/tables \
     -H "Authorization: Bearer {token}" \
     -H "Content-Type: application/json" \
     -d '{"table_number":1,"password":"1234"}'
   ```
   - 기대: 201 Created, table_number=1

3. **테이블 로그인** (Unit 1 API)
   ```bash
   curl -X POST http://localhost:8000/api/auth/table/login \
     -H "Content-Type: application/json" \
     -d '{"store_code":"store1","table_number":1,"password":"1234"}'
   ```
   - 기대: 200 OK, access_token 반환

4. **광고 목록 조회** (Unit 1 API)
   ```bash
   curl http://localhost:8000/api/customer/stores/1/advertisements \
     -H "Authorization: Bearer {table_token}"
   ```
   - 기대: 200 OK, 광고 목록 (빈 배열 또는 등록된 광고)

---

## 시나리오 2: 장바구니 → 결제 선택 → 주문 생성

### 설명
고객이 장바구니에 메뉴를 담고, 결제 방식을 선택한 후 주문을 생성

### 테스트 단계
1. **메뉴 조회** (Unit 2 API)
   ```bash
   curl http://localhost:8000/api/customer/stores/1/menus \
     -H "Authorization: Bearer {table_token}"
   ```

2. **장바구니 추가** (Frontend localStorage - 수동 테스트)
   - 메뉴 카드 터치 → 장바구니 추가
   - 장바구니 아이콘 배지 수량 확인

3. **주문 생성** (Unit 3 API)
   ```bash
   curl -X POST http://localhost:8000/api/orders \
     -H "Authorization: Bearer {table_token}" \
     -H "Content-Type: application/json" \
     -d '{"table_id":1,"payment_type":"SINGLE_PAY","items":[{"menu_id":1,"quantity":2}]}'
   ```
   - 기대: 201 Created, order_number 반환

---

## 시나리오 3: 이용 완료 처리

### 설명
매장 관리자가 테이블 이용 완료를 처리하고 세션이 종료되는지 확인

### 테스트 단계
1. **현재 세션 확인**
   ```bash
   curl http://localhost:8000/api/tables/1/session \
     -H "Authorization: Bearer {admin_token}"
   ```
   - 기대: 200 OK, is_active=true

2. **이용 완료 처리**
   ```bash
   curl -X POST http://localhost:8000/api/tables/1/complete \
     -H "Authorization: Bearer {admin_token}"
   ```
   - 기대: 200 OK, "이용 완료 처리되었습니다."

3. **세션 확인 (종료됨)**
   ```bash
   curl http://localhost:8000/api/tables/1/session \
     -H "Authorization: Bearer {admin_token}"
   ```
   - 기대: 404 (활성 세션 없음)

---

## 시나리오 4: 사다리 타기 미니게임 (Frontend 수동 테스트)

### 테스트 단계
1. 장바구니에서 "주문하기" 클릭
2. 결제 방식 선택 팝업 확인
3. 오른쪽 상단 🎲 버튼 클릭
4. 인원 수 선택 (예: 4명)
5. "시작!" 버튼 클릭
6. 사다리 애니메이션 확인 (Canvas 렌더링)
7. 꽝 결과 표시 확인 (빨간색 강조)
8. 5초 카운트다운 확인
9. 자동으로 결제 방식 선택 팝업 복귀 확인

### 검증 항목
- [ ] 인원 선택 UI 정상 표시 (2~10명)
- [ ] 사다리 Canvas 렌더링 정상
- [ ] 애니메이션 부드럽게 동작
- [ ] 꽝 결과 강조 연출
- [ ] 5초 카운트다운 정확
- [ ] 팝업 복귀 정상

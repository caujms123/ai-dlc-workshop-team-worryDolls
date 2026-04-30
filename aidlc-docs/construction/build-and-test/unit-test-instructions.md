# Unit Test Execution - Unit 4

## Backend 단위 테스트

### 실행
```bash
cd backend
pytest tests/test_table.py -v
```

### 테스트 목록 (6개)

| 테스트 | 설명 | 검증 항목 |
|---|---|---|
| test_create_table_success | 정상 테이블 등록 | ID 생성, table_number 확인 |
| test_create_table_duplicate_number | 중복 번호 등록 거부 | 409 Conflict |
| test_get_tables_with_session | 세션 포함 목록 조회 | 세션 정보 포함 확인 |
| test_complete_table_success | 정상 이용 완료 | 세션 종료, 메시지 확인 |
| test_complete_table_no_active_session | 활성 세션 없을 때 | 404 에러 |
| test_get_existing_session | 기존 세션 반환 | create 미호출 확인 |
| test_create_new_session | 새 세션 생성 | create 호출 확인 |

### 기대 결과
- **총 테스트**: 7개
- **통과**: 7개
- **실패**: 0개

---

## Frontend 단위 테스트

### 실행
```bash
cd frontend/customer
npm run test
```

### 테스트 목록 (8개)

| 테스트 | 설명 | 검증 항목 |
|---|---|---|
| addItem - 새 메뉴 추가 | 장바구니에 새 항목 추가 | items 길이, menuId |
| addItem - 동일 메뉴 수량 증가 | 같은 메뉴 추가 시 수량++ | quantity 2 |
| addItem - localStorage 저장 | 추가 시 persist | setItem 호출 |
| updateQuantity - 수량 변경 | 수량 직접 변경 | quantity 값 |
| updateQuantity - 수량 0 제거 | 수량 0이면 삭제 | items 길이 0 |
| removeItem | 항목 제거 | 해당 항목 없음 |
| clearCart | 전체 비우기 | isEmpty true |
| totalAmount 계산 | 총 금액 계산 | 정확한 금액 |

### 기대 결과
- **총 테스트**: 8개
- **통과**: 8개
- **실패**: 0개

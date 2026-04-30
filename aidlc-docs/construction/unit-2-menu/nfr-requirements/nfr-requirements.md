# Unit 2: NFR Requirements - 메뉴 관리

---

## 1. 성능 요구사항

| ID | 요구사항 | 목표값 |
|---|---|---|
| NFR-PERF-01 | 메뉴 목록 조회 API 응답 시간 | 500ms 이내 |
| NFR-PERF-02 | 메뉴 등록/수정 API 응답 시간 | 1초 이내 (이미지 업로드 포함) |
| NFR-PERF-03 | 고객용 메뉴 조회 API 응답 시간 | 300ms 이내 |
| NFR-PERF-04 | 카테고리 CRUD API 응답 시간 | 200ms 이내 |

## 2. 보안 요구사항

| ID | 요구사항 | 구현 방식 |
|---|---|---|
| NFR-SEC-01 | 메뉴 관리 접근 제어 | STORE_ADMIN 역할 필수 (Unit 1 AuthMiddleware) |
| NFR-SEC-02 | 매장 스코프 검증 | 자기 매장의 메뉴만 관리 가능 |
| NFR-SEC-03 | 고객 메뉴 조회 | TABLE 역할 또는 공개 (인증된 테이블) |
| NFR-SEC-04 | 이미지 업로드 보안 | Unit 1 FileUploadService 활용 |
| NFR-SEC-05 | 입력값 검증 | Pydantic 스키마, 가격 범위 검증 |

## 3. 사용성 요구사항 (Customer Frontend)

| ID | 요구사항 | 목표값 |
|---|---|---|
| NFR-UX-01 | 터치 타겟 크기 | 최소 44x44px |
| NFR-UX-02 | 메뉴 카드 이미지 로딩 | lazy loading 적용 |
| NFR-UX-03 | 카테고리 전환 | 즉시 (클라이언트 사이드 필터링) |

## 4. Security Extension 적용

| 규칙 | 적용 여부 | Unit 2 관련 사항 |
|---|---|---|
| SECURITY-05 (입력 검증) | ✅ | Pydantic 스키마, 가격/길이 검증 |
| SECURITY-08 (접근 제어) | ✅ | STORE_ADMIN 역할 검증, 매장 스코프 |
| SECURITY-15 (예외 처리) | ✅ | 카테고리 삭제 시 메뉴 존재 검증 |
| 기타 | Unit 1에서 공통 처리 | AuthMiddleware, 로깅, 에러 핸들러 |

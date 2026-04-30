# Unit 4: NFR Requirements - 고객 UI + 테이블 관리

---

## 1. 성능 요구사항

| ID | 요구사항 | 목표값 |
|---|---|---|
| NFR-PERF-01 | 광고 화면 로딩 시간 | 2초 이내 (이미지 포함) |
| NFR-PERF-02 | 광고 슬라이드 전환 | 즉시 (CSS transition) |
| NFR-PERF-03 | 장바구니 조작 응답 | 즉시 (로컬 처리) |
| NFR-PERF-04 | 사다리 타기 애니메이션 | 60fps 유지 |
| NFR-PERF-05 | 테이블 API 응답 시간 | 300ms 이내 |

## 2. 사용성 요구사항

| ID | 요구사항 | 목표값 |
|---|---|---|
| NFR-UX-01 | 터치 타겟 크기 | 최소 44x44px |
| NFR-UX-02 | 광고 화면 터치 반응 | 즉시 (1초 이내 메뉴 이동) |
| NFR-UX-03 | 비활성 자동 복귀 | 2분 후 광고 화면 |
| NFR-UX-04 | 사다리 타기 효과음 | 볼륨 조절 가능 또는 음소거 옵션 |
| NFR-UX-05 | 장바구니 데이터 유지 | 페이지 새로고침 시에도 유지 (localStorage) |

## 3. 보안 요구사항

| ID | 요구사항 | 구현 방식 |
|---|---|---|
| NFR-SEC-01 | 테이블 인증 | JWT 토큰 (TABLE 역할) |
| NFR-SEC-02 | 자격 증명 저장 | localStorage (토큰 + 자격 증명) |
| NFR-SEC-03 | 테이블 관리 권한 | STORE_ADMIN 역할 필수 |

## 4. Security Extension 적용

| 규칙 | 적용 여부 | Unit 4 관련 사항 |
|---|---|---|
| SECURITY-05 (입력 검증) | ✅ | 테이블 번호/비밀번호 검증 |
| SECURITY-08 (접근 제어) | ✅ | TABLE/STORE_ADMIN 역할 검증 |
| SECURITY-12 (인증 관리) | ✅ | 테이블 비밀번호 bcrypt 해싱 |
| SECURITY-15 (예외 처리) | ✅ | 이용 완료 실패 시 롤백 |

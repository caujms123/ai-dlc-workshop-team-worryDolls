# Unit 3: NFR Requirements - 주문 + SSE

---

## 1. 성능 요구사항

| ID | 요구사항 | 목표값 |
|---|---|---|
| NFR-PERF-01 | 주문 생성 API 응답 시간 | 1초 이내 |
| NFR-PERF-02 | SSE 이벤트 전달 지연 | 2초 이내 |
| NFR-PERF-03 | 주문 목록 조회 API 응답 시간 | 500ms 이내 |
| NFR-PERF-04 | 주문 상태 변경 API 응답 시간 | 300ms 이내 |
| NFR-PERF-05 | 과거 주문 이력 조회 | 1초 이내 |

## 2. 확장성 요구사항

| ID | 요구사항 | 목표값 |
|---|---|---|
| NFR-SCALE-01 | 동시 SSE 연결 (관리자) | 매장당 최대 10개 |
| NFR-SCALE-02 | 동시 SSE 연결 (고객) | 테이블당 최대 3개 |
| NFR-SCALE-03 | 동시 주문 처리 | 50~100 테이블 동시 주문 |
| NFR-SCALE-04 | 주문 이력 보관 | 무제한 (영구 보존) |

## 3. 보안 요구사항

| ID | 요구사항 | 구현 방식 |
|---|---|---|
| NFR-SEC-01 | 주문 생성 권한 | TABLE 역할 필수 |
| NFR-SEC-02 | 주문 관리 권한 | STORE_ADMIN 역할 필수 |
| NFR-SEC-03 | SSE 연결 인증 | JWT 토큰 기반 인증 |
| NFR-SEC-04 | 매장 스코프 | 자기 매장의 주문만 접근 |
| NFR-SEC-05 | 주문 데이터 무결성 | 트랜잭션 처리 |

## 4. 가용성 요구사항

| ID | 요구사항 | 구현 방식 |
|---|---|---|
| NFR-AVAIL-01 | SSE 연결 복구 | 클라이언트 자동 재연결 (EventSource 기본) |
| NFR-AVAIL-02 | SSE keep-alive | 30초 간격 ping |
| NFR-AVAIL-03 | 주문 데이터 보존 | 트랜잭션 + 이력 이동 원자성 보장 |

## 5. Security Extension 적용

| 규칙 | 적용 여부 | Unit 3 관련 사항 |
|---|---|---|
| SECURITY-05 (입력 검증) | ✅ | 주문 항목 검증, 상태 전이 검증 |
| SECURITY-08 (접근 제어) | ✅ | TABLE/STORE_ADMIN 역할 검증, SSE 인증 |
| SECURITY-13 (무결성) | ✅ | 주문 데이터 트랜잭션, 이력 이동 원자성 |
| SECURITY-15 (예외 처리) | ✅ | 주문 생성 실패 시 롤백, SSE 연결 오류 처리 |

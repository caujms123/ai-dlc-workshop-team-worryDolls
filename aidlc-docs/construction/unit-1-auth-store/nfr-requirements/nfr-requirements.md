# Unit 1: NFR Requirements - 인증 + 매장 + 관리자 + 광고

---

## 1. 성능 요구사항

| ID | 요구사항 | 목표값 |
|---|---|---|
| NFR-PERF-01 | 로그인 API 응답 시간 | 500ms 이내 (bcrypt 해싱 포함) |
| NFR-PERF-02 | 매장/관리자 CRUD API 응답 시간 | 300ms 이내 |
| NFR-PERF-03 | 광고 이미지 업로드 응답 시간 | 2초 이내 (5MB 기준) |
| NFR-PERF-04 | 광고 목록 조회 응답 시간 | 200ms 이내 |
| NFR-PERF-05 | JWT 토큰 검증 시간 | 10ms 이내 |

## 2. 보안 요구사항

| ID | 요구사항 | 구현 방식 |
|---|---|---|
| NFR-SEC-01 | 비밀번호 해싱 | bcrypt (cost factor: 12) |
| NFR-SEC-02 | JWT 토큰 서명 | HS256, 환경변수에서 시크릿 키 로드 |
| NFR-SEC-03 | 로그인 시도 제한 | 5회 실패 시 15분 잠금 |
| NFR-SEC-04 | RBAC | 미들웨어 레벨에서 역할 검증 |
| NFR-SEC-05 | 입력값 검증 | Pydantic 스키마 기반 자동 검증 |
| NFR-SEC-06 | SQL Injection 방지 | SQLAlchemy ORM (파라미터화된 쿼리) |
| NFR-SEC-07 | 파일 업로드 보안 | Content-Type 검증, 확장자 화이트리스트, 크기 제한 |
| NFR-SEC-08 | 에러 응답 보안 | 프로덕션에서 스택 트레이스 숨김 |
| NFR-SEC-09 | CORS 정책 | 허용된 오리진만 접근 (와일드카드 금지) |
| NFR-SEC-10 | HTTP 보안 헤더 | CSP, HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy |

## 3. 가용성 요구사항

| ID | 요구사항 | 목표값 |
|---|---|---|
| NFR-AVAIL-01 | 서비스 가용성 | 영업시간 내 99% |
| NFR-AVAIL-02 | 에러 복구 | 적절한 에러 메시지 + 자동 재시도 안내 |

## 4. 확장성 요구사항

| ID | 요구사항 | 목표값 |
|---|---|---|
| NFR-SCALE-01 | 동시 관리자 접속 | 50명 이상 |
| NFR-SCALE-02 | 매장 수 | 10개 이상 |
| NFR-SCALE-03 | 매장당 관리자 수 | 10명 이상 |

## 5. 유지보수성 요구사항

| ID | 요구사항 | 구현 방식 |
|---|---|---|
| NFR-MAINT-01 | 계층형 아키텍처 | Router → Service → Repository |
| NFR-MAINT-02 | API 문서 자동 생성 | FastAPI Swagger/OpenAPI |
| NFR-MAINT-03 | 구조화된 로깅 | Python logging, JSON 형식 |
| NFR-MAINT-04 | DB 마이그레이션 | Alembic |

## 6. Security Extension 적용 (SECURITY 규칙)

| 규칙 | 적용 여부 | Unit 1 관련 사항 |
|---|---|---|
| SECURITY-03 (앱 로깅) | ✅ 적용 | 구조화된 로깅 프레임워크, 민감 데이터 로깅 금지 |
| SECURITY-04 (HTTP 헤더) | ✅ 적용 | CSP, HSTS, X-Content-Type-Options 등 설정 |
| SECURITY-05 (입력 검증) | ✅ 적용 | Pydantic 스키마, 파라미터화된 쿼리 |
| SECURITY-08 (접근 제어) | ✅ 적용 | AuthMiddleware, RBAC, 매장 스코프 검증 |
| SECURITY-09 (보안 강화) | ✅ 적용 | 기본 자격 증명 없음, 에러 응답 보안 |
| SECURITY-10 (공급망) | ✅ 적용 | requirements.txt 버전 고정, lock 파일 |
| SECURITY-11 (보안 설계) | ✅ 적용 | 인증 모듈 분리, Rate Limiting |
| SECURITY-12 (인증 관리) | ✅ 적용 | bcrypt, 세션 만료, brute-force 방지 |
| SECURITY-13 (무결성) | ✅ 적용 | 안전한 역직렬화 (Pydantic) |
| SECURITY-15 (예외 처리) | ✅ 적용 | GlobalErrorHandler, fail-closed |
| SECURITY-01,02,06,07,14 | N/A | 온프레미스 환경, 인프라 규칙 해당 없음 |

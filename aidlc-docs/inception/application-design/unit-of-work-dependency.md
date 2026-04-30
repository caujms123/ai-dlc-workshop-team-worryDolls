# 테이블오더 서비스 - Unit 의존성 매트릭스

---

## 1. Unit 간 의존성 매트릭스

| Unit (행이 의존) | Unit 1 (인증+매장) | Unit 2 (메뉴) | Unit 3 (주문+SSE) | Unit 4 (고객UI+테이블) |
|---|---|---|---|---|
| **Unit 1** | - | - | - | - |
| **Unit 2** | ★ AuthMiddleware, FileUploadService | - | - | - |
| **Unit 3** | ★ AuthMiddleware | MenuService (검증) | - | TableService (세션) |
| **Unit 4** | ★ AuthMiddleware, AuthService (로그인) | - | OrderService (주문 생성) | - |

> ★ = 핵심 의존성 (반드시 먼저 완성 필요)

---

## 2. 의존성 다이어그램

```
+-------------------+
| Unit 1            |
| 인증+매장+관리자  |
| +광고+파일업로드  |
| (기반 인프라)     |
+-------------------+
    |           |
    v           v
+--------+  +-------------------+
| Unit 2 |  | Unit 4            |
| 메뉴   |  | 고객UI+테이블     |
+--------+  +-------------------+
    |           |
    v           v
+-------------------+
| Unit 3            |
| 주문+SSE          |
| (Menu, Table 의존)|
+-------------------+
```

---

## 3. 병렬 작업 전략

### Phase 1: 기반 구축 (모든 Unit 동시 시작)
- **Unit 1**: AuthMiddleware, JWT, bcrypt, Store/Admin CRUD, FileUpload → **최우선**
- **Unit 2**: Category/Menu 모델 및 서비스 (Auth 없이 로직 먼저 개발)
- **Unit 3**: Order/SSE 모델 및 서비스 (Auth 없이 로직 먼저 개발)
- **Unit 4**: Table 모델, 고객 UI 컴포넌트 (사다리 타기 등 독립 개발)

### Phase 2: 통합 (Unit 1 완성 후)
- **Unit 2**: AuthMiddleware 적용, FileUploadService 연동
- **Unit 3**: AuthMiddleware 적용, Menu/Table 서비스 연동
- **Unit 4**: AuthService 연동 (테이블 로그인), Order API 연동

### Phase 3: 최종 통합
- 전체 Unit 통합 테스트
- SSE 실시간 통신 End-to-End 테스트
- 주문 플로우 전체 테스트 (고객 주문 → 관리자 모니터링)

---

## 4. 공유 리소스

### Unit 1이 제공하는 공통 모듈 (다른 Unit에서 사용)
| 모듈 | 사용 Unit | 용도 |
|---|---|---|
| AuthMiddleware | Unit 2, 3, 4 | API 인증/인가 |
| RateLimiter | Unit 2, 3, 4 | 로그인 시도 제한 |
| GlobalErrorHandler | Unit 2, 3, 4 | 전역 에러 처리 |
| FileUploadService | Unit 2 | 메뉴 이미지 업로드 |
| database.py | Unit 2, 3, 4 | DB 연결 설정 |
| config.py | Unit 2, 3, 4 | 앱 설정 |

### 공유 인터페이스 계약
| 제공 Unit | 소비 Unit | 인터페이스 | 설명 |
|---|---|---|---|
| Unit 1 | Unit 3, 4 | `verify_token(token) → UserInfo` | JWT 검증 |
| Unit 2 | Unit 3 | `get_menu(menu_id) → Menu` | 주문 시 메뉴 검증 |
| Unit 4 | Unit 3 | `get_current_session(table_id) → Session` | 주문 시 세션 확인 |
| Unit 3 | Unit 4 | `create_order(data) → Order` | 고객 주문 생성 |
| Unit 3 | Unit 4 | `move_to_history(session_id)` | 이용 완료 시 이력 이동 |

---

## 5. 위험 요소 및 완화 방안

| 위험 | 영향 Unit | 완화 방안 |
|---|---|---|
| Unit 1 지연 시 전체 차단 | Unit 2, 3, 4 | Unit 1의 AuthMiddleware를 최우선 개발. 다른 Unit은 Mock Auth로 먼저 개발 |
| Unit 3 ↔ Unit 4 순환 의존 | Unit 3, 4 | 인터페이스 계약을 먼저 합의. OrderRepository 직접 접근으로 순환 해결 |
| SSE 통합 복잡도 | Unit 3, 4 | SSE 이벤트 스키마를 먼저 정의하고 공유 |
| 사다리 타기 UX 복잡도 | Unit 4 | 기본 로직 먼저 구현, 애니메이션/효과음은 후순위 |

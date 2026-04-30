# Unit 3: Code Generation Summary - 주문 + SSE

## 생성 파일 목록

### Backend (14 파일)
| 파일 | 용도 |
|---|---|
| `app/models/order.py` | Order, OrderItem, OrderHistory 모델 |
| `app/schemas/order.py` | Pydantic 요청/응답 스키마 |
| `app/schemas/sse.py` | SSE 이벤트 스키마 |
| `app/repositories/order_repo.py` | OrderRepository (데이터 접근) |
| `app/services/order_service.py` | OrderService (비즈니스 로직) |
| `app/services/sse_service.py` | SSEManager (실시간 이벤트) |
| `app/routers/order.py` | 주문 API 라우터 (7 엔드포인트) |
| `app/routers/sse.py` | SSE 스트림 라우터 (2 엔드포인트) |
| `app/middleware/auth.py` | 인증 미들웨어 Stub |
| `app/database.py` | DB 연결 설정 |
| `app/config.py` | 앱 설정 |
| `alembic/versions/003_create_order_tables.py` | DB 마이그레이션 |
| `__init__.py` 파일들 | 패키지 초기화 (7개) |

### Backend Tests (4 파일)
| 파일 | 테스트 수 |
|---|---|
| `tests/test_order_repo.py` | 15개 |
| `tests/test_order_service.py` | 12개 |
| `tests/test_sse_service.py` | 10개 |
| `tests/test_order_router.py` | 11개 |
| `tests/test_sse_router.py` | 4개 |
| `tests/conftest.py` | 공통 Fixture |

### Frontend Admin (5 파일)
| 파일 | 용도 |
|---|---|
| `views/OrderView.vue` | 실시간 주문 대시보드 |
| `components/order/TableOrderCard.vue` | 테이블 주문 카드 |
| `components/order/OrderDetailPanel.vue` | 주문 상세 패널 |
| `stores/orderStore.js` | Pinia Store |
| `services/orderApi.js` | API 호출 서비스 |

### Frontend Customer (5 파일)
| 파일 | 용도 |
|---|---|
| `views/OrderView.vue` | 주문 확정 화면 |
| `views/OrderHistoryView.vue` | 주문 내역 조회 |
| `components/OrderConfirm.vue` | 주문 요약 위젯 |
| `stores/orderStore.js` | Pinia Store |
| `services/orderApi.js` | API 호출 서비스 |

### Frontend Tests (7 파일)
| 파일 | 대상 |
|---|---|
| `admin/tests/components/order/TableOrderCard.spec.js` | 카드 컴포넌트 |
| `admin/tests/components/order/OrderDetailPanel.spec.js` | 상세 패널 |
| `admin/tests/views/OrderView.spec.js` | 대시보드 뷰 |
| `admin/tests/stores/orderStore.spec.js` | Admin Store |
| `customer/tests/views/OrderView.spec.js` | 주문 확정 뷰 |
| `customer/tests/views/OrderHistoryView.spec.js` | 주문 내역 뷰 |
| `customer/tests/stores/orderStore.spec.js` | Customer Store |

## Story 커버리지

| Story | 구현 상태 |
|---|---|
| US-MA-07 (실시간 주문 대시보드) | ✅ Backend + Admin Frontend + SSE |
| US-MA-08 (주문 상세 조회) | ✅ Backend + Admin Frontend |
| US-MA-09 (주문 상태 변경) | ✅ Backend + Admin Frontend + SSE |
| US-MA-11 (주문 삭제) | ✅ Backend + Admin Frontend + SSE |
| US-MA-12 (이용 완료 처리) | ✅ Backend + Admin Frontend + SSE |
| US-MA-13 (과거 주문 내역) | ✅ Backend + Admin Frontend |
| US-CU-09 (주문 확정) | ✅ Backend + Customer Frontend |
| US-CU-10 (주문 내역 조회) | ✅ Backend + Customer Frontend + SSE |

**8/8 스토리 100% 커버리지**

## Security Extension 준수

| 규칙 | 상태 | 구현 |
|---|---|---|
| SECURITY-03 | ✅ | 구조화된 로깅 (logging 모듈) |
| SECURITY-05 | ✅ | Pydantic 입력 검증, 상태 전이 검증 |
| SECURITY-08 | ✅ | JWT 인증, RBAC (TABLE/STORE_ADMIN), 매장 스코프 |
| SECURITY-09 | ✅ | HTTPException으로 안전한 에러 응답 |
| SECURITY-11 | ✅ | 보안 로직 분리 (AuthMiddleware) |
| SECURITY-12 | ✅ | JWT 토큰 검증, SSE 연결 인증 |
| SECURITY-13 | ✅ | 트랜잭션 무결성 (주문 생성, 이력 이동) |
| SECURITY-15 | ✅ | 전역 에러 핸들러, 트랜잭션 롤백 |
| SECURITY-01 | N/A | 인프라 레벨 (온프레미스) |
| SECURITY-02 | N/A | 네트워크 인프라 |
| SECURITY-04 | N/A | Unit 1 미들웨어에서 처리 |
| SECURITY-06 | N/A | 인프라 레벨 |
| SECURITY-07 | N/A | 네트워크 인프라 |
| SECURITY-10 | N/A | Build & Test 단계에서 처리 |
| SECURITY-14 | N/A | 운영 단계 |

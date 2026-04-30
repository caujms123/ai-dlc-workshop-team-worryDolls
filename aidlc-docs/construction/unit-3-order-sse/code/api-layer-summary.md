# Unit 3: API Layer Summary

## 생성 파일
- `backend/app/routers/order.py` - 주문 API 라우터
- `backend/app/routers/sse.py` - SSE 스트림 라우터
- `backend/app/middleware/auth.py` - 인증 미들웨어 Stub (Unit 1 교체 예정)

## 엔드포인트 목록

### Order Router
| Method | Path | 역할 | Story |
|---|---|---|---|
| POST | `/api/orders` | TABLE | US-CU-09 |
| GET | `/api/tables/{id}/orders` | TABLE, STORE_ADMIN | US-CU-10 |
| GET | `/api/stores/{id}/orders` | STORE_ADMIN | US-MA-07 |
| PATCH | `/api/orders/{id}/status` | STORE_ADMIN | US-MA-09 |
| DELETE | `/api/orders/{id}` | STORE_ADMIN | US-MA-11 |
| POST | `/api/tables/{id}/complete` | STORE_ADMIN | US-MA-12 |
| GET | `/api/tables/{id}/order-history` | STORE_ADMIN | US-MA-13 |

### SSE Router
| Method | Path | 역할 | Story |
|---|---|---|---|
| GET | `/api/sse/admin/stores/{id}/orders` | STORE_ADMIN | US-MA-07 |
| GET | `/api/sse/customer/tables/{id}/orders` | TABLE | US-CU-10 |

## 테스트
- `backend/tests/test_order_router.py` - 11개 테스트 케이스
- `backend/tests/test_sse_router.py` - 4개 테스트 케이스

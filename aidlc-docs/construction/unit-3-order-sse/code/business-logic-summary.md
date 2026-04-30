# Unit 3: Business Logic Summary

## 생성 파일
- `backend/app/services/order_service.py` - OrderService 클래스
- `backend/app/services/sse_service.py` - SSEManager 클래스 (Singleton)

## OrderService 메서드
| 메서드 | 용도 | Story |
|---|---|---|
| `create_order` | 주문 생성 (검증+스냅샷+번호생성+SSE) | US-CU-09 |
| `get_table_orders` | 테이블 현재 세션 주문 조회 | US-CU-10 |
| `get_store_orders` | 매장 전체 활성 주문 조회 | US-MA-07 |
| `update_order_status` | 주문 상태 변경 (전이 검증+SSE) | US-MA-09 |
| `delete_order` | 주문 삭제 (관리자 직권+SSE) | US-MA-11 |
| `move_to_history` | 세션 주문 이력 이동 (트랜잭션+SSE) | US-MA-12 |
| `get_order_history` | 과거 주문 이력 조회 | US-MA-13 |
| `get_table_total` | 테이블 총 주문액 계산 | - |

## SSEManager 메서드
| 메서드 | 용도 |
|---|---|
| `subscribe_admin` | 관리자 SSE 구독 (매장당 최대 10개) |
| `unsubscribe_admin` | 관리자 SSE 구독 해제 |
| `subscribe_customer` | 고객 SSE 구독 (테이블당 최대 3개) |
| `unsubscribe_customer` | 고객 SSE 구독 해제 |
| `publish_to_store` | 매장 관리자에게 이벤트 발행 |
| `publish_to_table` | 테이블 고객에게 이벤트 발행 |

## 테스트
- `backend/tests/test_order_service.py` - 12개 테스트 케이스
- `backend/tests/test_sse_service.py` - 10개 테스트 케이스

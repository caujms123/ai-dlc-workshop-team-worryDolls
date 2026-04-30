# Unit 3: Repository Layer Summary

## 생성 파일
- `backend/app/repositories/order_repo.py` - OrderRepository 클래스

## 메서드 목록
| 메서드 | 용도 |
|---|---|
| `create` | 주문 생성 |
| `get_by_id` | ID로 주문 조회 (items 포함 옵션) |
| `get_by_session` | 세션별 주문 목록 |
| `get_by_store` | 매장별 활성 주문 목록 |
| `get_by_table_and_session` | 테이블+세션별 주문 목록 |
| `update_status` | 주문 상태 업데이트 |
| `delete_order` | 주문 삭제 (CASCADE) |
| `count_today_orders` | 오늘 주문 수 (번호 생성용) |
| `create_order_items` | 주문 항목 일괄 생성 |
| `get_order_items` | 주문 항목 조회 |
| `delete_order_items` | 주문 항목 일괄 삭제 |
| `create_history` | 주문 이력 생성 |
| `get_history_by_table` | 테이블별 이력 조회 (날짜 필터) |
| `get_history_by_store` | 매장별 이력 조회 (날짜 필터) |
| `get_table_total` | 테이블 총 주문액 계산 |

## 테스트
- `backend/tests/test_order_repo.py` - 15개 테스트 케이스

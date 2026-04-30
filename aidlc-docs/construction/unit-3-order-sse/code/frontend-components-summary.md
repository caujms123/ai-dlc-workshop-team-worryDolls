# Unit 3: Frontend Components Summary

## Admin Frontend

### Views
| 파일 | 목적 | Story |
|---|---|---|
| `views/OrderView.vue` | 실시간 주문 대시보드 (그리드) | US-MA-07, US-MA-08 |

### Components
| 파일 | 목적 | Story |
|---|---|---|
| `components/order/TableOrderCard.vue` | 테이블별 주문 카드 | US-MA-07 |
| `components/order/OrderDetailPanel.vue` | 주문 상세 패널 (상태변경/삭제/이용완료/이력) | US-MA-08~13 |

### Store & Service
| 파일 | 목적 |
|---|---|
| `stores/orderStore.js` | Pinia Store (SSE 연결, 주문 상태 관리) |
| `services/orderApi.js` | API 호출 (조회/상태변경/삭제/이용완료/이력) |

## Customer Frontend

### Views
| 파일 | 목적 | Story |
|---|---|---|
| `views/OrderView.vue` | 주문 확정 화면 | US-CU-09 |
| `views/OrderHistoryView.vue` | 주문 내역 조회 (SSE 실시간) | US-CU-10 |

### Components
| 파일 | 목적 |
|---|---|
| `components/OrderConfirm.vue` | 주문 요약 위젯 (재사용) |

### Store & Service
| 파일 | 목적 |
|---|---|
| `stores/orderStore.js` | Pinia Store (주문 조회, SSE) |
| `services/orderApi.js` | API 호출 (주문 생성, 조회) |

## 테스트
- Admin: 4개 테스트 파일 (TableOrderCard, OrderDetailPanel, OrderView, orderStore)
- Customer: 3개 테스트 파일 (OrderView, OrderHistoryView, orderStore)

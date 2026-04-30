# 테이블오더 서비스 - 컴포넌트 의존성

---

## 1. 의존성 매트릭스

| 서비스 (행이 사용) | Auth | Store | Admin | Ad | Menu | Order | Table | SSE | FileUpload |
|---|---|---|---|---|---|---|---|---|---|
| **AuthService** | - | R | R | - | - | - | R | - | - |
| **StoreService** | - | - | - | - | - | - | - | - | - |
| **AdminService** | R | - | - | - | - | - | - | - | - |
| **AdvertisementService** | - | - | - | - | - | - | - | - | R |
| **MenuService** | - | - | - | - | - | - | - | - | R |
| **OrderService** | - | - | - | - | R | - | R | W | - |
| **TableService** | - | - | - | - | - | R | - | - | - |
| **SSEService** | - | - | - | - | - | - | - | - | - |
| **FileUploadService** | - | - | - | - | - | - | - | - | - |

> R = Read (조회), W = Write (이벤트 발행)

---

## 2. 의존성 다이어그램

```
+------------------+
| AuthMiddleware   |----> AuthService
+------------------+          |
                              v
                    +------------------+
                    | StoreRepository  |
                    | AdminRepository  |
                    | TableRepository  |
                    +------------------+

+------------------+     +------------------+
| StoreService     |     | AdminService     |
| (독립적)         |     |   |              |
+------------------+     |   v              |
                         | AuthService      |
                         | (비밀번호 해싱)  |
                         +------------------+

+------------------+     +------------------+
| AdvertisementSvc |---->| FileUploadSvc    |
+------------------+     +------------------+
                              ^
+------------------+          |
| MenuService      |----------+
+------------------+

+------------------+     +------------------+
| OrderService     |---->| SSEService       |
|   |              |     +------------------+
|   v              |
| TableService     |
| MenuService (검증)|
+------------------+

+------------------+     +------------------+
| TableService     |---->| OrderService     |
| (이용 완료)      |     | (이력 이동)      |
+------------------+     +------------------+
```

---

## 3. 순환 의존성 분석

**잠재적 순환**: OrderService ↔ TableService
- OrderService → TableService: 세션 확인/시작
- TableService → OrderService: 이용 완료 시 이력 이동

**해결 방안**: 이벤트 기반 분리
- TableService.complete_table()이 OrderService.move_to_history()를 직접 호출하는 대신
- OrderRepository를 직접 사용하여 이력 이동 처리
- 또는 별도의 SessionService를 도입하여 중재

---

## 4. 데이터 흐름

### 4.1 주문 생성 플로우
```
Customer UI
    |
    v
OrderRouter.create_order()
    |
    v
AuthMiddleware (테이블 인증 확인)
    |
    v
OrderService.create_order()
    |-- TableService.get_current_session() (세션 확인)
    |-- TableService.start_session() (첫 주문이면 세션 시작)
    |-- MenuService.get_menu() (메뉴 유효성 검증)
    |-- OrderRepository.create() (DB 저장)
    |-- SSEService.publish_order_event() (관리자 알림)
    v
Response (주문 번호)
```

### 4.2 이용 완료 플로우
```
Admin UI
    |
    v
TableRouter.complete_table()
    |
    v
AuthMiddleware (매장 관리자 인증 확인)
    |
    v
TableService.complete_table()
    |-- OrderRepository.move_to_history() (주문 이력 이동)
    |-- TableRepository.end_session() (세션 종료)
    |-- SSEService.publish_order_event() (대시보드 갱신)
    v
Response (성공)
```

### 4.3 SSE 실시간 통신 플로우
```
Admin/Customer UI
    |
    v (SSE 연결)
SSERouter.subscribe()
    |
    v
SSEService.subscribe_admin/customer()
    |
    v (연결 유지, 이벤트 대기)
    
... (주문 생성/상태 변경 발생) ...

OrderService
    |
    v
SSEService.publish_order_event()
    |
    v (구독자에게 이벤트 전달)
Admin/Customer UI (실시간 업데이트)
```

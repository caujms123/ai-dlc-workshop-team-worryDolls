# Unit 3: NFR Design Patterns - 주문 + SSE

---

## 1. SSE (Server-Sent Events) 패턴

### 1.1 SSE 연결 관리자 (Singleton)
```python
class SSEManager:
    """매장별/테이블별 SSE 연결 관리"""
    def __init__(self):
        self._admin_connections: dict[int, list[asyncio.Queue]] = {}  # store_id → queues
        self._customer_connections: dict[int, list[asyncio.Queue]] = {}  # table_id → queues

    async def subscribe_admin(self, store_id: int) -> asyncio.Queue:
        queue = asyncio.Queue()
        self._admin_connections.setdefault(store_id, []).append(queue)
        return queue

    async def unsubscribe_admin(self, store_id: int, queue: asyncio.Queue):
        if store_id in self._admin_connections:
            self._admin_connections[store_id].remove(queue)

    async def publish_to_store(self, store_id: int, event: dict):
        for queue in self._admin_connections.get(store_id, []):
            await queue.put(event)

    async def publish_to_table(self, table_id: int, event: dict):
        for queue in self._customer_connections.get(table_id, []):
            await queue.put(event)

sse_manager = SSEManager()  # 싱글톤
```

### 1.2 SSE 엔드포인트 패턴
```python
@router.get("/sse/admin/stores/{store_id}/orders")
async def admin_order_stream(store_id: int, current_user = Depends(require_role("STORE_ADMIN"))):
    queue = await sse_manager.subscribe_admin(store_id)
    try:
        async def event_generator():
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30)
                    yield f"data: {json.dumps(event)}\n\n"
                except asyncio.TimeoutError:
                    yield f": keep-alive\n\n"  # ping
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    finally:
        await sse_manager.unsubscribe_admin(store_id, queue)
```

---

## 2. 트랜잭션 패턴

### 2.1 주문 생성 트랜잭션
```python
async def create_order(self, order_data, db: AsyncSession):
    async with db.begin():  # 트랜잭션 시작
        # 1. 세션 확인/생성
        session = await self.table_service.get_or_create_session(order_data.table_id, db)
        # 2. 메뉴 검증 + 스냅샷
        items = await self._validate_and_snapshot_items(order_data.items, db)
        # 3. 주문 생성
        order = Order(...)
        db.add(order)
        # 4. 주문 항목 생성
        for item in items:
            db.add(OrderItem(order=order, ...))
        await db.flush()  # ID 생성
    # 트랜잭션 커밋 후 SSE 발행 (트랜잭션 외부)
    await sse_manager.publish_to_store(order.store_id, {...})
    return order
```

### 2.2 이력 이동 트랜잭션
```python
async def move_to_history(self, session_id: int, db: AsyncSession):
    async with db.begin():
        orders = await self.order_repo.get_by_session(session_id, db)
        for order in orders:
            items = await self.order_item_repo.get_by_order(order.id, db)
            history = OrderHistory(
                items_json=json.dumps([item.to_dict() for item in items]),
                completed_at=datetime.utcnow(),
                ...
            )
            db.add(history)
            for item in items:
                await db.delete(item)
            await db.delete(order)
```

---

## 3. 주문 번호 생성 패턴

```python
async def generate_order_number(self, store_id: int, db: AsyncSession) -> str:
    today = date.today().strftime("%Y%m%d")
    # 해당 매장의 오늘 주문 수 조회
    count = await self.order_repo.count_today_orders(store_id, today, db)
    return f"ORD-{today}-{count + 1:04d}"
```

---

## 4. 상태 전이 패턴

```python
VALID_TRANSITIONS = {
    OrderStatus.PENDING: [OrderStatus.PREPARING],
    OrderStatus.PREPARING: [OrderStatus.COMPLETED],
    OrderStatus.COMPLETED: [],
}

def validate_status_transition(current: OrderStatus, new: OrderStatus):
    if new not in VALID_TRANSITIONS.get(current, []):
        raise HTTPException(422, f"Invalid transition: {current} → {new}")
```

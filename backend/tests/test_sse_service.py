"""SSEService 단위 테스트."""

import asyncio

import pytest

from app.services.sse_service import (
    SSEManager,
    MAX_ADMIN_CONNECTIONS_PER_STORE,
    MAX_CUSTOMER_CONNECTIONS_PER_TABLE,
)


@pytest.fixture
def sse_manager() -> SSEManager:
    """테스트용 SSEManager 인스턴스."""
    return SSEManager()


# ── 관리자 SSE 구독/해제 테스트 ──


@pytest.mark.asyncio
async def test_subscribe_admin(sse_manager: SSEManager):
    """관리자 SSE 구독 테스트."""
    queue = await sse_manager.subscribe_admin(store_id=1)
    assert isinstance(queue, asyncio.Queue)
    assert sse_manager.get_admin_connection_count(1) == 1


@pytest.mark.asyncio
async def test_unsubscribe_admin(sse_manager: SSEManager):
    """관리자 SSE 구독 해제 테스트."""
    queue = await sse_manager.subscribe_admin(store_id=1)
    await sse_manager.unsubscribe_admin(store_id=1, queue=queue)
    assert sse_manager.get_admin_connection_count(1) == 0


@pytest.mark.asyncio
async def test_admin_max_connections(sse_manager: SSEManager):
    """관리자 SSE 최대 연결 수 초과 테스트."""
    for _ in range(MAX_ADMIN_CONNECTIONS_PER_STORE):
        await sse_manager.subscribe_admin(store_id=1)
    with pytest.raises(ConnectionError):
        await sse_manager.subscribe_admin(store_id=1)


# ── 고객 SSE 구독/해제 테스트 ──


@pytest.mark.asyncio
async def test_subscribe_customer(sse_manager: SSEManager):
    """고객 SSE 구독 테스트."""
    queue = await sse_manager.subscribe_customer(table_id=1)
    assert isinstance(queue, asyncio.Queue)
    assert sse_manager.get_customer_connection_count(1) == 1


@pytest.mark.asyncio
async def test_unsubscribe_customer(sse_manager: SSEManager):
    """고객 SSE 구독 해제 테스트."""
    queue = await sse_manager.subscribe_customer(table_id=1)
    await sse_manager.unsubscribe_customer(table_id=1, queue=queue)
    assert sse_manager.get_customer_connection_count(1) == 0


@pytest.mark.asyncio
async def test_customer_max_connections(sse_manager: SSEManager):
    """고객 SSE 최대 연결 수 초과 테스트."""
    for _ in range(MAX_CUSTOMER_CONNECTIONS_PER_TABLE):
        await sse_manager.subscribe_customer(table_id=1)
    with pytest.raises(ConnectionError):
        await sse_manager.subscribe_customer(table_id=1)


# ── 이벤트 발행 테스트 ──


@pytest.mark.asyncio
async def test_publish_to_store(sse_manager: SSEManager):
    """매장 이벤트 발행 테스트."""
    queue = await sse_manager.subscribe_admin(store_id=1)
    event = {"event_type": "new_order", "data": {"order_id": 1}}
    await sse_manager.publish_to_store(store_id=1, event=event)
    received = await queue.get()
    assert received["event_type"] == "new_order"
    assert received["data"]["order_id"] == 1


@pytest.mark.asyncio
async def test_publish_to_table(sse_manager: SSEManager):
    """테이블 이벤트 발행 테스트."""
    queue = await sse_manager.subscribe_customer(table_id=1)
    event = {"event_type": "order_status_changed", "data": {"order_id": 1}}
    await sse_manager.publish_to_table(table_id=1, event=event)
    received = await queue.get()
    assert received["event_type"] == "order_status_changed"


@pytest.mark.asyncio
async def test_publish_to_multiple_subscribers(sse_manager: SSEManager):
    """다중 구독자 이벤트 발행 테스트."""
    q1 = await sse_manager.subscribe_admin(store_id=1)
    q2 = await sse_manager.subscribe_admin(store_id=1)
    event = {"event_type": "new_order", "data": {"order_id": 1}}
    await sse_manager.publish_to_store(store_id=1, event=event)
    r1 = await q1.get()
    r2 = await q2.get()
    assert r1 == r2 == event


@pytest.mark.asyncio
async def test_publish_to_empty_store(sse_manager: SSEManager):
    """구독자 없는 매장에 이벤트 발행 테스트 (에러 없이 무시)."""
    await sse_manager.publish_to_store(store_id=999, event={"event_type": "test"})
    # 에러 없이 정상 완료


@pytest.mark.asyncio
async def test_connection_count(sse_manager: SSEManager):
    """연결 수 조회 테스트."""
    assert sse_manager.get_admin_connection_count(1) == 0
    await sse_manager.subscribe_admin(store_id=1)
    await sse_manager.subscribe_admin(store_id=1)
    assert sse_manager.get_admin_connection_count(1) == 2
    assert sse_manager.get_customer_connection_count(1) == 0

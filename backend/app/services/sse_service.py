"""SSE (Server-Sent Events) 연결 관리 서비스.

Singleton 패턴으로 매장별/테이블별 SSE 연결을 관리합니다.
- 관리자: store_id 기반 구독 (매장당 최대 10개)
- 고객: table_id 기반 구독 (테이블당 최대 3개)
"""

import asyncio
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

# 연결 수 제한
MAX_ADMIN_CONNECTIONS_PER_STORE = 10
MAX_CUSTOMER_CONNECTIONS_PER_TABLE = 3


class SSEManager:
    """매장별/테이블별 SSE 연결 관리자 (Singleton)."""

    def __init__(self) -> None:
        self._admin_connections: dict[int, list[asyncio.Queue]] = {}
        self._customer_connections: dict[int, list[asyncio.Queue]] = {}

    # ── 관리자 SSE ──

    async def subscribe_admin(self, store_id: int) -> asyncio.Queue:
        """관리자 SSE 구독 등록.

        Args:
            store_id: 매장 ID

        Returns:
            이벤트 수신용 asyncio.Queue

        Raises:
            ConnectionError: 최대 연결 수 초과 시
        """
        connections = self._admin_connections.setdefault(store_id, [])
        if len(connections) >= MAX_ADMIN_CONNECTIONS_PER_STORE:
            logger.warning(
                "관리자 SSE 연결 수 초과: store_id=%s, current=%s",
                store_id,
                len(connections),
            )
            raise ConnectionError(
                f"매장당 최대 {MAX_ADMIN_CONNECTIONS_PER_STORE}개 연결만 허용됩니다"
            )
        queue: asyncio.Queue = asyncio.Queue()
        connections.append(queue)
        logger.info(
            "관리자 SSE 구독: store_id=%s, total=%s",
            store_id,
            len(connections),
        )
        return queue

    async def unsubscribe_admin(self, store_id: int, queue: asyncio.Queue) -> None:
        """관리자 SSE 구독 해제."""
        connections = self._admin_connections.get(store_id, [])
        if queue in connections:
            connections.remove(queue)
            logger.info(
                "관리자 SSE 구독 해제: store_id=%s, remaining=%s",
                store_id,
                len(connections),
            )
        if not connections and store_id in self._admin_connections:
            del self._admin_connections[store_id]

    # ── 고객 SSE ──

    async def subscribe_customer(self, table_id: int) -> asyncio.Queue:
        """고객 SSE 구독 등록.

        Args:
            table_id: 테이블 ID

        Returns:
            이벤트 수신용 asyncio.Queue

        Raises:
            ConnectionError: 최대 연결 수 초과 시
        """
        connections = self._customer_connections.setdefault(table_id, [])
        if len(connections) >= MAX_CUSTOMER_CONNECTIONS_PER_TABLE:
            logger.warning(
                "고객 SSE 연결 수 초과: table_id=%s, current=%s",
                table_id,
                len(connections),
            )
            raise ConnectionError(
                f"테이블당 최대 {MAX_CUSTOMER_CONNECTIONS_PER_TABLE}개 연결만 허용됩니다"
            )
        queue: asyncio.Queue = asyncio.Queue()
        connections.append(queue)
        logger.info(
            "고객 SSE 구독: table_id=%s, total=%s",
            table_id,
            len(connections),
        )
        return queue

    async def unsubscribe_customer(self, table_id: int, queue: asyncio.Queue) -> None:
        """고객 SSE 구독 해제."""
        connections = self._customer_connections.get(table_id, [])
        if queue in connections:
            connections.remove(queue)
            logger.info(
                "고객 SSE 구독 해제: table_id=%s, remaining=%s",
                table_id,
                len(connections),
            )
        if not connections and table_id in self._customer_connections:
            del self._customer_connections[table_id]

    # ── 이벤트 발행 ──

    async def publish_to_store(self, store_id: int, event: dict[str, Any]) -> None:
        """매장의 모든 관리자 SSE 연결에 이벤트 발행.

        전송 실패한 연결은 자동 제거됩니다.
        """
        connections = self._admin_connections.get(store_id, [])
        failed: list[asyncio.Queue] = []
        for queue in connections:
            try:
                await queue.put(event)
            except Exception:
                logger.warning("관리자 SSE 이벤트 전송 실패: store_id=%s", store_id)
                failed.append(queue)
        # 실패한 연결 제거
        for q in failed:
            await self.unsubscribe_admin(store_id, q)
        if connections:
            logger.debug(
                "관리자 SSE 이벤트 발행: store_id=%s, event_type=%s, recipients=%s",
                store_id,
                event.get("event_type"),
                len(connections) - len(failed),
            )

    async def publish_to_table(self, table_id: int, event: dict[str, Any]) -> None:
        """테이블의 모든 고객 SSE 연결에 이벤트 발행.

        전송 실패한 연결은 자동 제거됩니다.
        """
        connections = self._customer_connections.get(table_id, [])
        failed: list[asyncio.Queue] = []
        for queue in connections:
            try:
                await queue.put(event)
            except Exception:
                logger.warning("고객 SSE 이벤트 전송 실패: table_id=%s", table_id)
                failed.append(queue)
        for q in failed:
            await self.unsubscribe_customer(table_id, q)
        if connections:
            logger.debug(
                "고객 SSE 이벤트 발행: table_id=%s, event_type=%s, recipients=%s",
                table_id,
                event.get("event_type"),
                len(connections) - len(failed),
            )

    # ── 상태 조회 ──

    def get_admin_connection_count(self, store_id: int) -> int:
        """매장의 관리자 SSE 연결 수 조회."""
        return len(self._admin_connections.get(store_id, []))

    def get_customer_connection_count(self, table_id: int) -> int:
        """테이블의 고객 SSE 연결 수 조회."""
        return len(self._customer_connections.get(table_id, []))


# 싱글톤 인스턴스
sse_manager = SSEManager()

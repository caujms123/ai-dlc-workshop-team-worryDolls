"""테이블 Repository (Unit 4)"""

from datetime import datetime
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.table import TableInfo, TableSession


class TableRepository:
    """테이블 데이터 접근 레이어"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, table: TableInfo) -> TableInfo:
        self.db.add(table)
        await self.db.flush()
        await self.db.refresh(table)
        return table

    async def get_by_id(self, table_id: int) -> Optional[TableInfo]:
        result = await self.db.execute(
            select(TableInfo).where(TableInfo.id == table_id)
        )
        return result.scalar_one_or_none()

    async def get_by_store_and_number(self, store_id: int, table_number: int) -> Optional[TableInfo]:
        result = await self.db.execute(
            select(TableInfo).where(
                and_(TableInfo.store_id == store_id, TableInfo.table_number == table_number)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_store(self, store_id: int) -> list[TableInfo]:
        result = await self.db.execute(
            select(TableInfo)
            .where(TableInfo.store_id == store_id)
            .order_by(TableInfo.table_number)
        )
        return list(result.scalars().all())

    async def update(self, table: TableInfo) -> TableInfo:
        await self.db.flush()
        await self.db.refresh(table)
        return table


class TableSessionRepository:
    """테이블 세션 데이터 접근 레이어"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, session: TableSession) -> TableSession:
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def get_active_session(self, table_id: int) -> Optional[TableSession]:
        result = await self.db.execute(
            select(TableSession).where(
                and_(TableSession.table_id == table_id, TableSession.is_active == True)
            )
        )
        return result.scalar_one_or_none()

    async def end_session(self, session: TableSession) -> TableSession:
        session.is_active = False
        session.ended_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(session)
        return session

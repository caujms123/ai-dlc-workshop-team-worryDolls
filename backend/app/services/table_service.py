"""테이블 서비스 (Unit 4)"""

import structlog
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.models.table import TableInfo, TableSession
from app.repositories.table_repo import TableRepository, TableSessionRepository
from app.schemas.table import TableCreate, TableUpdate

logger = structlog.get_logger()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TableService:
    """테이블 및 세션 비즈니스 로직"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.table_repo = TableRepository(db)
        self.session_repo = TableSessionRepository(db)

    async def create_table(self, store_id: int, data: TableCreate) -> TableInfo:
        """테이블 등록"""
        # 중복 확인
        existing = await self.table_repo.get_by_store_and_number(store_id, data.table_number)
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"테이블 번호 {data.table_number}은(는) 이미 등록되어 있습니다."
            )

        table = TableInfo(
            store_id=store_id,
            table_number=data.table_number,
            password_hash=pwd_context.hash(data.password),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        table = await self.table_repo.create(table)

        logger.info("table_created", store_id=store_id, table_number=data.table_number, table_id=table.id)
        return table

    async def get_tables(self, store_id: int) -> list[dict]:
        """매장의 테이블 목록 조회 (현재 세션 정보 포함)"""
        tables = await self.table_repo.get_by_store(store_id)
        result = []
        for table in tables:
            session = await self.session_repo.get_active_session(table.id)
            result.append({
                "id": table.id,
                "store_id": table.store_id,
                "table_number": table.table_number,
                "is_active": table.is_active,
                "current_session": session,
                "created_at": table.created_at,
                "updated_at": table.updated_at,
            })
        return result

    async def get_table_by_id(self, table_id: int) -> TableInfo:
        """테이블 ID로 조회"""
        table = await self.table_repo.get_by_id(table_id)
        if not table:
            raise HTTPException(status_code=404, detail="테이블을 찾을 수 없습니다.")
        return table

    async def update_table(self, table_id: int, data: TableUpdate) -> TableInfo:
        """테이블 수정 (비밀번호 변경)"""
        table = await self.get_table_by_id(table_id)
        if data.password:
            table.password_hash = pwd_context.hash(data.password)
        table.updated_at = datetime.utcnow()
        return await self.table_repo.update(table)

    async def get_current_session(self, table_id: int) -> TableSession:
        """현재 활성 세션 조회"""
        session = await self.session_repo.get_active_session(table_id)
        if not session:
            raise HTTPException(status_code=404, detail="활성 세션이 없습니다.")
        return session

    async def get_or_create_session(self, table_id: int, store_id: int) -> TableSession:
        """현재 세션 조회 또는 새 세션 생성 (주문 생성 시 호출)"""
        session = await self.session_repo.get_active_session(table_id)
        if session:
            return session

        # 새 세션 생성
        new_session = TableSession(
            table_id=table_id,
            store_id=store_id,
            started_at=datetime.utcnow(),
            is_active=True,
        )
        new_session = await self.session_repo.create(new_session)
        logger.info("session_started", table_id=table_id, session_id=new_session.id)
        return new_session

    async def complete_table(self, table_id: int) -> dict:
        """테이블 이용 완료 처리"""
        session = await self.session_repo.get_active_session(table_id)
        if not session:
            raise HTTPException(status_code=404, detail="활성 세션이 없습니다.")

        session_id = session.id

        # 세션 종료
        await self.session_repo.end_session(session)

        logger.info("table_completed", table_id=table_id, session_id=session_id)

        return {
            "message": "이용 완료 처리되었습니다.",
            "table_id": table_id,
            "session_id": session_id,
        }

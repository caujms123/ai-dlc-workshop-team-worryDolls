"""Unit 4: 테이블 서비스 단위 테스트"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from fastapi import HTTPException

from app.services.table_service import TableService
from app.schemas.table import TableCreate, TableUpdate
from app.models.table import TableInfo, TableSession


@pytest.fixture
def mock_db():
    db = AsyncMock()
    return db


@pytest.fixture
def table_service(mock_db):
    service = TableService(mock_db)
    service.table_repo = AsyncMock()
    service.session_repo = AsyncMock()
    return service


class TestCreateTable:
    """테이블 등록 테스트"""

    @pytest.mark.asyncio
    async def test_create_table_success(self, table_service):
        """정상적인 테이블 등록"""
        table_service.table_repo.get_by_store_and_number.return_value = None
        table_service.table_repo.create.return_value = TableInfo(
            id=1, store_id=1, table_number=1,
            password_hash="hashed", is_active=True,
            created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        )

        data = TableCreate(table_number=1, password="1234")
        result = await table_service.create_table(store_id=1, data=data)

        assert result.id == 1
        assert result.table_number == 1
        table_service.table_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_table_duplicate_number(self, table_service):
        """중복 테이블 번호 등록 시 409 에러"""
        table_service.table_repo.get_by_store_and_number.return_value = TableInfo(
            id=1, store_id=1, table_number=1,
            password_hash="hashed", is_active=True,
            created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        )

        data = TableCreate(table_number=1, password="1234")
        with pytest.raises(HTTPException) as exc_info:
            await table_service.create_table(store_id=1, data=data)

        assert exc_info.value.status_code == 409


class TestGetTables:
    """테이블 목록 조회 테스트"""

    @pytest.mark.asyncio
    async def test_get_tables_with_session(self, table_service):
        """세션 정보 포함 테이블 목록 조회"""
        table_service.table_repo.get_by_store.return_value = [
            TableInfo(
                id=1, store_id=1, table_number=1,
                password_hash="h", is_active=True,
                created_at=datetime.utcnow(), updated_at=datetime.utcnow()
            )
        ]
        table_service.session_repo.get_active_session.return_value = TableSession(
            id=10, table_id=1, store_id=1,
            started_at=datetime.utcnow(), is_active=True
        )

        result = await table_service.get_tables(store_id=1)

        assert len(result) == 1
        assert result[0]["table_number"] == 1
        assert result[0]["current_session"] is not None


class TestCompleteTable:
    """이용 완료 처리 테스트"""

    @pytest.mark.asyncio
    async def test_complete_table_success(self, table_service):
        """정상적인 이용 완료 처리"""
        session = TableSession(
            id=10, table_id=1, store_id=1,
            started_at=datetime.utcnow(), is_active=True
        )
        table_service.session_repo.get_active_session.return_value = session
        table_service.session_repo.end_session.return_value = session

        result = await table_service.complete_table(table_id=1)

        assert result["message"] == "이용 완료 처리되었습니다."
        assert result["table_id"] == 1
        assert result["session_id"] == 10
        table_service.session_repo.end_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_table_no_active_session(self, table_service):
        """활성 세션 없을 때 404 에러"""
        table_service.session_repo.get_active_session.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await table_service.complete_table(table_id=1)

        assert exc_info.value.status_code == 404


class TestGetOrCreateSession:
    """세션 조회/생성 테스트"""

    @pytest.mark.asyncio
    async def test_get_existing_session(self, table_service):
        """기존 활성 세션 반환"""
        existing = TableSession(
            id=10, table_id=1, store_id=1,
            started_at=datetime.utcnow(), is_active=True
        )
        table_service.session_repo.get_active_session.return_value = existing

        result = await table_service.get_or_create_session(table_id=1, store_id=1)

        assert result.id == 10
        table_service.session_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_new_session(self, table_service):
        """활성 세션 없으면 새 세션 생성"""
        table_service.session_repo.get_active_session.return_value = None
        table_service.session_repo.create.return_value = TableSession(
            id=11, table_id=1, store_id=1,
            started_at=datetime.utcnow(), is_active=True
        )

        result = await table_service.get_or_create_session(table_id=1, store_id=1)

        assert result.id == 11
        table_service.session_repo.create.assert_called_once()

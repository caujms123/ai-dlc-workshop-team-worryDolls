"""테이블 API 라우터 (Unit 4)"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.table import (
    TableCreate, TableUpdate, TableResponse,
    TableWithSessionResponse, TableSessionResponse, CompleteTableResponse,
)
from app.services.table_service import TableService
from app.database import get_db

router = APIRouter(prefix="/api", tags=["tables"])


def get_table_service(db: AsyncSession = Depends(get_db)) -> TableService:
    return TableService(db)


@router.post("/stores/{store_id}/tables", response_model=TableResponse, status_code=201)
async def create_table(
    store_id: int,
    data: TableCreate,
    service: TableService = Depends(get_table_service),
):
    """테이블 등록 (매장 관리자)"""
    table = await service.create_table(store_id, data)
    return table


@router.get("/stores/{store_id}/tables", response_model=list[TableWithSessionResponse])
async def get_tables(
    store_id: int,
    service: TableService = Depends(get_table_service),
):
    """매장의 테이블 목록 조회 (현재 세션 정보 포함)"""
    return await service.get_tables(store_id)


@router.put("/tables/{table_id}", response_model=TableResponse)
async def update_table(
    table_id: int,
    data: TableUpdate,
    service: TableService = Depends(get_table_service),
):
    """테이블 수정 (비밀번호 변경)"""
    return await service.update_table(table_id, data)


@router.get("/tables/{table_id}/session", response_model=TableSessionResponse)
async def get_current_session(
    table_id: int,
    service: TableService = Depends(get_table_service),
):
    """현재 활성 세션 조회"""
    return await service.get_current_session(table_id)


@router.post("/tables/{table_id}/complete", response_model=CompleteTableResponse)
async def complete_table(
    table_id: int,
    service: TableService = Depends(get_table_service),
):
    """테이블 이용 완료 처리 (매장 관리자)"""
    return await service.complete_table(table_id)

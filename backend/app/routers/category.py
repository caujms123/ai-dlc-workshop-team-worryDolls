"""Category API router."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import get_db
from backend.app.schemas.category import (
    CategoryCreate,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdate,
)
from backend.app.services.category_service import CategoryService

logger = logging.getLogger(__name__)

router = APIRouter()

# Service dependency
_category_service = CategoryService()


def get_category_service() -> CategoryService:
    """Dependency for CategoryService."""
    return _category_service


# Type aliases for cleaner signatures
CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
DbSessionDep = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "/stores/{store_id}/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="카테고리 등록",
    description="매장에 새로운 메뉴 카테고리를 등록합니다. (STORE_ADMIN 권한 필요)",
)
async def create_category(
    store_id: Annotated[int, Path(gt=0, description="매장 ID")],
    data: CategoryCreate,
    service: CategoryServiceDep,
    db: DbSessionDep,
    # TODO: current_user: Annotated[UserInfo, Depends(get_current_admin_user)]
    # Unit 1 AuthMiddleware 통합 시 활성화
):
    """Create a new category for a store.

    SECURITY-08: Requires STORE_ADMIN role and store scope verification.
    """
    # TODO: Verify current_user.store_id == store_id (SECURITY-08)
    category = await service.create_category(
        store_id=store_id, data=data, db=db
    )
    return category


@router.get(
    "/stores/{store_id}/categories",
    response_model=CategoryListResponse,
    summary="카테고리 목록 조회",
    description="매장의 카테고리 목록을 조회합니다.",
)
async def get_categories(
    store_id: Annotated[int, Path(gt=0, description="매장 ID")],
    service: CategoryServiceDep,
    db: DbSessionDep,
):
    """Get all categories for a store."""
    categories = await service.get_categories(store_id=store_id, db=db)
    return CategoryListResponse(
        categories=[CategoryResponse.model_validate(c) for c in categories],
        total=len(categories),
    )


@router.put(
    "/categories/{category_id}",
    response_model=CategoryResponse,
    summary="카테고리 수정",
    description="카테고리 이름을 수정합니다. (STORE_ADMIN 권한 필요)",
)
async def update_category(
    category_id: Annotated[int, Path(gt=0, description="카테고리 ID")],
    data: CategoryUpdate,
    service: CategoryServiceDep,
    db: DbSessionDep,
    # TODO: current_user: Annotated[UserInfo, Depends(get_current_admin_user)]
    store_id: int = 1,  # TODO: Extract from current_user.store_id
):
    """Update a category.

    SECURITY-08: Requires STORE_ADMIN role and store scope verification.
    """
    updated = await service.update_category(
        category_id=category_id, store_id=store_id, data=data, db=db
    )
    return updated


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="카테고리 삭제",
    description="카테고리를 삭제합니다. 메뉴가 존재하면 삭제할 수 없습니다. (STORE_ADMIN 권한 필요)",
)
async def delete_category(
    category_id: Annotated[int, Path(gt=0, description="카테고리 ID")],
    service: CategoryServiceDep,
    db: DbSessionDep,
    # TODO: current_user: Annotated[UserInfo, Depends(get_current_admin_user)]
    store_id: int = 1,  # TODO: Extract from current_user.store_id
):
    """Delete a category.

    BR-CAT-02: Returns 409 if category has menus.
    SECURITY-08: Requires STORE_ADMIN role and store scope verification.
    """
    await service.delete_category(
        category_id=category_id, store_id=store_id, db=db
    )

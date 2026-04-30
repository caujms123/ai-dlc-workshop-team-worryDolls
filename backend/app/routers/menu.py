"""Menu API router."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Path, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.menu import (
    CategoryWithMenusResponse,
    CustomerMenuResponse,
    MenuCreate,
    MenuListResponse,
    MenuOrderUpdate,
    MenuResponse,
    MenuUpdate,
)
from app.services.menu_service import MenuService

logger = logging.getLogger(__name__)

router = APIRouter()

# Service dependency
_menu_service = MenuService()


def get_menu_service() -> MenuService:
    """Dependency for MenuService."""
    return _menu_service


# Type aliases
MenuServiceDep = Annotated[MenuService, Depends(get_menu_service)]
DbSessionDep = Annotated[AsyncSession, Depends(get_db)]


# ============================================================
# Admin Endpoints (STORE_ADMIN role required)
# ============================================================


@router.post(
    "/stores/{store_id}/menus",
    response_model=MenuResponse,
    status_code=status.HTTP_201_CREATED,
    summary="메뉴 등록",
    description="매장에 새로운 메뉴를 등록합니다. 이미지 파일 업로드를 포함할 수 있습니다. (STORE_ADMIN 권한 필요)",
)
async def create_menu(
    store_id: Annotated[int, Path(gt=0, description="매장 ID")],
    name: Annotated[str, Form(min_length=2, max_length=100, description="메뉴명")],
    price: Annotated[int, Form(ge=0, le=10_000_000, description="가격")],
    category_id: Annotated[int, Form(gt=0, description="카테고리 ID")],
    service: MenuServiceDep,
    db: DbSessionDep,
    description: Annotated[str | None, Form(max_length=1000, description="메뉴 설명")] = None,
    image: Annotated[UploadFile | None, File(description="메뉴 이미지 (JPG, PNG)")] = None,
    # TODO: current_user: Annotated[UserInfo, Depends(get_current_admin_user)]
):
    """Create a new menu item with optional image upload.

    SECURITY-05: Input validation via Form parameters.
    SECURITY-08: Requires STORE_ADMIN role and store scope verification.
    """
    # TODO: Verify current_user.store_id == store_id (SECURITY-08)
    data = MenuCreate(
        name=name,
        price=price,
        description=description,
        category_id=category_id,
    )
    menu = await service.create_menu(
        store_id=store_id, data=data, db=db, image=image
    )
    return menu


@router.get(
    "/stores/{store_id}/menus",
    response_model=MenuListResponse,
    summary="메뉴 목록 조회 (관리자)",
    description="매장의 메뉴 목록을 조회합니다. 카테고리별 필터링이 가능합니다. (STORE_ADMIN 권한 필요)",
)
async def get_menus(
    store_id: Annotated[int, Path(gt=0, description="매장 ID")],
    service: MenuServiceDep,
    db: DbSessionDep,
    category_id: Annotated[int | None, Query(gt=0, description="카테고리 ID 필터")] = None,
    # TODO: current_user: Annotated[UserInfo, Depends(get_current_admin_user)]
):
    """Get menus for a store, optionally filtered by category."""
    menus = await service.get_menus(
        store_id=store_id, db=db, category_id=category_id
    )
    return MenuListResponse(
        menus=[MenuResponse.model_validate(m) for m in menus],
        total=len(menus),
    )


@router.get(
    "/menus/{menu_id}",
    response_model=MenuResponse,
    summary="메뉴 상세 조회",
    description="특정 메뉴의 상세 정보를 조회합니다. (STORE_ADMIN 권한 필요)",
)
async def get_menu(
    menu_id: Annotated[int, Path(gt=0, description="메뉴 ID")],
    service: MenuServiceDep,
    db: DbSessionDep,
    # TODO: current_user: Annotated[UserInfo, Depends(get_current_admin_user)]
    store_id: int = 1,  # TODO: Extract from current_user.store_id
):
    """Get a single menu item."""
    menu = await service.get_menu(
        menu_id=menu_id, store_id=store_id, db=db
    )
    return menu


@router.put(
    "/menus/{menu_id}",
    response_model=MenuResponse,
    summary="메뉴 수정",
    description="메뉴 정보를 수정합니다. 이미지 교체를 포함할 수 있습니다. (STORE_ADMIN 권한 필요)",
)
async def update_menu(
    menu_id: Annotated[int, Path(gt=0, description="메뉴 ID")],
    service: MenuServiceDep,
    db: DbSessionDep,
    name: Annotated[str | None, Form(min_length=2, max_length=100, description="메뉴명")] = None,
    price: Annotated[int | None, Form(ge=0, le=10_000_000, description="가격")] = None,
    description: Annotated[str | None, Form(max_length=1000, description="메뉴 설명")] = None,
    category_id: Annotated[int | None, Form(gt=0, description="카테고리 ID")] = None,
    is_available: Annotated[bool | None, Form(description="판매 가능 여부")] = None,
    image: Annotated[UploadFile | None, File(description="새 메뉴 이미지")] = None,
    # TODO: current_user: Annotated[UserInfo, Depends(get_current_admin_user)]
    store_id: int = 1,  # TODO: Extract from current_user.store_id
):
    """Update a menu item with optional image replacement.

    BR-MENU-03: Old image is deleted when new image is uploaded.
    """
    data = MenuUpdate(
        name=name,
        price=price,
        description=description,
        category_id=category_id,
        is_available=is_available,
    )
    updated = await service.update_menu(
        menu_id=menu_id, store_id=store_id, data=data, db=db, image=image
    )
    return updated


@router.delete(
    "/menus/{menu_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="메뉴 삭제",
    description="메뉴를 삭제합니다. 이미지 파일도 함께 삭제됩니다. (STORE_ADMIN 권한 필요)",
)
async def delete_menu(
    menu_id: Annotated[int, Path(gt=0, description="메뉴 ID")],
    service: MenuServiceDep,
    db: DbSessionDep,
    # TODO: current_user: Annotated[UserInfo, Depends(get_current_admin_user)]
    store_id: int = 1,  # TODO: Extract from current_user.store_id
):
    """Delete a menu item and its image file."""
    await service.delete_menu(
        menu_id=menu_id, store_id=store_id, db=db
    )


@router.put(
    "/menus/{menu_id}/order",
    response_model=MenuResponse,
    summary="메뉴 노출 순서 변경",
    description="메뉴의 노출 순서를 변경합니다. (STORE_ADMIN 권한 필요)",
)
async def update_menu_order(
    menu_id: Annotated[int, Path(gt=0, description="메뉴 ID")],
    data: MenuOrderUpdate,
    service: MenuServiceDep,
    db: DbSessionDep,
    # TODO: current_user: Annotated[UserInfo, Depends(get_current_admin_user)]
    store_id: int = 1,  # TODO: Extract from current_user.store_id
):
    """Update a menu's display order.

    BR-MENU-04: Sibling menus are reordered automatically.
    """
    updated = await service.update_menu_order(
        menu_id=menu_id, store_id=store_id, data=data, db=db
    )
    return updated


# ============================================================
# Customer Endpoints (TABLE role or public)
# ============================================================


@router.get(
    "/customer/stores/{store_id}/menus",
    response_model=CustomerMenuResponse,
    summary="고객용 메뉴 조회",
    description="고객용 메뉴를 카테고리별로 그룹화하여 조회합니다. 판매 가능한 메뉴만 표시됩니다.",
)
async def get_customer_menus(
    store_id: Annotated[int, Path(gt=0, description="매장 ID")],
    service: MenuServiceDep,
    db: DbSessionDep,
    # TODO: current_user: Annotated[UserInfo, Depends(get_current_table_user)]
):
    """Get menus grouped by category for customer view.

    BR-MENU-05: Only available menus, grouped by category.
    """
    result = await service.get_customer_menus(store_id=store_id, db=db)
    return CustomerMenuResponse(data=result)

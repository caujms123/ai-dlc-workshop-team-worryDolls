"""Menu Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, Field

from backend.app.schemas.category import CategoryResponse


class MenuCreate(BaseModel):
    """Schema for creating a new menu item. (SECURITY-05: Input validation)"""

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="메뉴명 (2~100자)",
        examples=["김치찌개"],
    )
    price: int = Field(
        ...,
        ge=0,
        le=10_000_000,
        description="가격 (0~10,000,000원)",
        examples=[9000],
    )
    description: str | None = Field(
        None,
        max_length=1000,
        description="메뉴 설명 (최대 1000자)",
        examples=["매콤한 김치찌개"],
    )
    category_id: int = Field(
        ...,
        gt=0,
        description="카테고리 ID",
        examples=[1],
    )


class MenuUpdate(BaseModel):
    """Schema for updating an existing menu item."""

    name: str | None = Field(
        None,
        min_length=2,
        max_length=100,
        description="메뉴명 (2~100자)",
    )
    price: int | None = Field(
        None,
        ge=0,
        le=10_000_000,
        description="가격 (0~10,000,000원)",
    )
    description: str | None = Field(
        None,
        max_length=1000,
        description="메뉴 설명 (최대 1000자)",
    )
    category_id: int | None = Field(
        None,
        gt=0,
        description="카테고리 ID",
    )
    is_available: bool | None = Field(
        None,
        description="판매 가능 여부",
    )


class MenuOrderUpdate(BaseModel):
    """Schema for updating menu display order."""

    display_order: int = Field(
        ...,
        ge=0,
        description="새로운 노출 순서",
        examples=[0],
    )


class MenuResponse(BaseModel):
    """Schema for menu response."""

    id: int
    store_id: int
    category_id: int
    name: str
    price: int
    description: str | None
    image_path: str | None
    display_order: int
    is_available: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MenuListResponse(BaseModel):
    """Schema for menu list response."""

    menus: list[MenuResponse]
    total: int


class CustomerMenuItemResponse(BaseModel):
    """Schema for customer-facing menu item (simplified)."""

    id: int
    name: str
    price: int
    description: str | None
    image_path: str | None

    model_config = {"from_attributes": True}


class CategoryWithMenusResponse(BaseModel):
    """Schema for category with its menus (customer view)."""

    category: CategoryResponse
    menus: list[CustomerMenuItemResponse]


class CustomerMenuResponse(BaseModel):
    """Schema for customer menu response (grouped by category)."""

    data: list[CategoryWithMenusResponse]

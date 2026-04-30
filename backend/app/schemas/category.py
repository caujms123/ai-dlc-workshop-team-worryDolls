"""Category Pydantic schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    """Schema for creating a new category. (SECURITY-05: Input validation)"""

    name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="카테고리명 (2~50자)",
        examples=["메인 메뉴"],
    )


class CategoryUpdate(BaseModel):
    """Schema for updating an existing category."""

    name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="카테고리명 (2~50자)",
        examples=["사이드 메뉴"],
    )


class CategoryResponse(BaseModel):
    """Schema for category response."""

    id: int
    store_id: int
    name: str
    display_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CategoryListResponse(BaseModel):
    """Schema for category list response."""

    categories: list[CategoryResponse]
    total: int

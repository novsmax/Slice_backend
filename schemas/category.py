from pydantic import Field
from typing import Optional
from schemas.base import BaseSchema, IDSchema, TimestampSchema


class CategoryBase(BaseSchema):
    """Базовые поля категории"""
    name: str = Field(..., min_length=1, max_length=100, description="Название категории")
    description: Optional[str] = Field(None, description="Описание категории")


class CategoryCreate(CategoryBase):
    """Схема для создания категории"""
    pass


class CategoryUpdate(BaseSchema):
    """Схема для обновления категории"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Название категории")
    description: Optional[str] = Field(None, description="Описание категории")


class CategoryInDB(CategoryBase, IDSchema, TimestampSchema):
    """Полная схема категории из БД"""
    pass


class Category(CategoryInDB):
    """Схема для возвращения категории в API"""
    pass
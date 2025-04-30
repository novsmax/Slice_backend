from pydantic import Field, HttpUrl
from typing import Optional
from schemas.base import BaseSchema, IDSchema, TimestampSchema


class BrandBase(BaseSchema):
    """Базовые поля бренда"""
    name: str = Field(..., min_length=1, max_length=100, description="Название бренда")
    description: Optional[str] = Field(None, description="Описание бренда")
    logo_url: Optional[str] = Field(None, description="URL логотипа бренда")


class BrandCreate(BrandBase):
    """Схема для создания бренда"""
    pass


class BrandUpdate(BaseSchema):
    """Схема для обновления бренда"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Название бренда")
    description: Optional[str] = Field(None, description="Описание бренда")
    logo_url: Optional[str] = Field(None, description="URL логотипа бренда")


class BrandInDB(BrandBase, IDSchema, TimestampSchema):
    """Полная схема бренда из БД"""
    pass


class Brand(BrandInDB):
    """Схема для возвращения бренда в API"""
    pass
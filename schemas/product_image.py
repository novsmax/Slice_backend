from pydantic import Field
from typing import Optional
from schemas.base import BaseSchema, IDSchema, TimestampSchema


class ProductImageBase(BaseSchema):
    """Базовые поля изображения товара"""
    image_url: str = Field(..., min_length=1, max_length=255, description="URL изображения")
    alt_text: Optional[str] = Field(None, max_length=255, description="Альтернативный текст")
    is_primary: bool = Field(False, description="Является ли изображение основным")
    display_order: int = Field(0, description="Порядок отображения")
    product_id: int = Field(..., description="ID товара, к которому относится изображение")


class ProductImageCreate(ProductImageBase):
    """Схема для создания изображения товара"""
    pass


class ProductImageUpdate(BaseSchema):
    """Схема для обновления изображения товара"""
    image_url: Optional[str] = Field(None, min_length=1, max_length=255, description="URL изображения")
    alt_text: Optional[str] = Field(None, max_length=255, description="Альтернативный текст")
    is_primary: Optional[bool] = Field(None, description="Является ли изображение основным")
    display_order: Optional[int] = Field(None, description="Порядок отображения")


class ProductImageInDB(ProductImageBase, IDSchema, TimestampSchema):
    """Полная схема изображения товара из БД"""
    pass


class ProductImage(ProductImageInDB):
    """Схема для возвращения изображения товара в API"""
    pass
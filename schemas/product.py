from pydantic import Field, validator
from typing import Optional, List
from schemas.base import BaseSchema, IDSchema, TimestampSchema
from schemas.category import Category
from schemas.brand import Brand
from schemas.product_image import ProductImage


class ProductBase(BaseSchema):
    """Базовые поля товара"""
    name: str = Field(..., min_length=1, max_length=255, description="Название товара")
    description: Optional[str] = Field(None, description="Описание товара")
    price: float = Field(..., gt=0, description="Цена товара")
    stock: int = Field(0, ge=0, description="Количество товара на складе")
    sku: Optional[str] = Field(None, max_length=50, description="Артикул товара")
    is_active: bool = Field(True, description="Активен ли товар (доступен для продажи)")
    category_id: Optional[int] = Field(None, description="ID категории товара")
    brand_id: Optional[int] = Field(None, description="ID бренда товара")


class ProductCreate(ProductBase):
    """Схема для создания товара"""
    pass


class ProductUpdate(BaseSchema):
    """Схема для обновления товара"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Название товара")
    description: Optional[str] = Field(None, description="Описание товара")
    price: Optional[float] = Field(None, gt=0, description="Цена товара")
    stock: Optional[int] = Field(None, ge=0, description="Количество товара на складе")
    sku: Optional[str] = Field(None, max_length=50, description="Артикул товара")
    is_active: Optional[bool] = Field(None, description="Активен ли товар (доступен для продажи)")
    category_id: Optional[int] = Field(None, description="ID категории товара")
    brand_id: Optional[int] = Field(None, description="ID бренда товара")


class ProductInDB(ProductBase, IDSchema, TimestampSchema):
    """Полная схема товара из БД"""
    pass


class ProductWithRelations(ProductInDB):
    """Схема товара с включенными связанными данными"""
    category: Optional[Category] = None
    brand: Optional[Brand] = None
    images: List[ProductImage] = []


class Product(ProductInDB):
    """Схема для возвращения товара в API (без связанных объектов)"""
    pass


class ProductDetail(ProductInDB):
    """Схема для детального представления товара (со связанными объектами)"""
    category: Optional[Category] = None
    brand: Optional[Brand] = None
    images: List[ProductImage] = []
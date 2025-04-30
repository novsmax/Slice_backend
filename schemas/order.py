from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime
from enum import Enum

from schemas.base import BaseSchema, IDSchema, TimestampSchema
from schemas.user import User


class OrderStatus(str, Enum):
    """Статусы заказа"""
    CART = "cart"  # Корзина (заказ еще не оформлен)
    NEW = "new"  # Новый заказ
    PROCESSING = "processing"  # Заказ в обработке
    SHIPPED = "shipped"  # Заказ отправлен
    DELIVERED = "delivered"  # Заказ доставлен
    CANCELED = "canceled"  # Заказ отменен


class OrderItemBase(BaseSchema):
    """Базовая схема элемента заказа"""
    product_id: int = Field(..., description="ID товара")
    quantity: int = Field(1, ge=1, description="Количество товара")


class OrderItemCreate(OrderItemBase):
    """Схема для создания элемента заказа (добавления в корзину)"""
    pass


class OrderItemUpdate(BaseSchema):
    """Схема для обновления элемента заказа"""
    quantity: Optional[int] = Field(None, ge=1, description="Количество товара")


class OrderItemInDB(BaseSchema):
    """Схема элемента заказа из БД"""
    id: int
    order_id: int
    product_id: Optional[int] = None
    quantity: int
    price: float
    product_name: str
    created_at: datetime
    updated_at: datetime


class OrderItem(OrderItemInDB):
    """Схема элемента заказа для API"""
    pass


class OrderBase(BaseSchema):
    """Базовая схема заказа"""
    shipping_address: Optional[str] = Field(None, max_length=500, description="Адрес доставки")
    phone_number: Optional[str] = Field(None, max_length=20, description="Номер телефона")
    notes: Optional[str] = Field(None, max_length=1000, description="Примечания к заказу")


class OrderCreate(OrderBase):
    """Схема для создания заказа (оформления корзины)"""
    pass


class OrderUpdate(BaseSchema):
    """Схема для обновления заказа"""
    shipping_address: Optional[str] = Field(None, max_length=500, description="Адрес доставки")
    phone_number: Optional[str] = Field(None, max_length=20, description="Номер телефона")
    notes: Optional[str] = Field(None, max_length=1000, description="Примечания к заказу")
    status: Optional[OrderStatus] = Field(None, description="Статус заказа")


class OrderInDB(BaseSchema):
    """Схема заказа из БД"""
    id: int
    user_id: int
    status: str
    total_amount: float
    shipping_address: Optional[str] = None
    phone_number: Optional[str] = None
    notes: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class Order(OrderInDB):
    """Схема заказа для API"""
    items: List[OrderItem] = []


class CartItemAdd(BaseSchema):
    """Схема для добавления товара в корзину"""
    product_id: int = Field(..., description="ID товара")
    quantity: int = Field(1, ge=1, description="Количество товара")


class CartResponse(BaseSchema):
    """Схема для корзины"""
    id: int
    status: str
    total_amount: float
    items: List[OrderItem] = []
    created_at: datetime
    updated_at: datetime
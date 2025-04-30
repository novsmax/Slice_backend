from sqlalchemy import Column, String, Integer, Float, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from datetime import datetime

from models.base import BaseModel


class OrderStatus(str, PyEnum):
    """Статусы заказа"""
    CART = "cart"  # Корзина (заказ еще не оформлен)
    NEW = "new"  # Новый заказ
    PROCESSING = "processing"  # Заказ в обработке
    SHIPPED = "shipped"  # Заказ отправлен
    DELIVERED = "delivered"  # Заказ доставлен
    CANCELED = "canceled"  # Заказ отменен


class Order(BaseModel):
    """
    Модель заказа
    """
    __tablename__ = "orders"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(20), default=OrderStatus.CART.value, nullable=False, index=True)
    total_amount = Column(Float, default=0.0, nullable=False)
    shipping_address = Column(String(500), nullable=True)
    phone_number = Column(String(20), nullable=True)
    notes = Column(String(1000), nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Отношения
    user = relationship("User", backref="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Order {self.id} - {self.status}>"
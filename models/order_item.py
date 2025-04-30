from sqlalchemy import Column, String, Integer, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from models.base import BaseModel


class OrderItem(BaseModel):
    """
    Модель элемента заказа
    """
    __tablename__ = "order_items"
    
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    quantity = Column(Integer, default=1, nullable=False)
    price = Column(Float, nullable=False) 
    product_name = Column(String(255), nullable=False)  
    
    # Отношения
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    
    def __repr__(self):
        return f"<OrderItem {self.product_name} x{self.quantity}>"
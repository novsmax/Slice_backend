from sqlalchemy import Column, String, Text, Integer, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from models.base import BaseModel


class Product(BaseModel):
    """
    Модель для товаров
    """
    __tablename__ = "products"

    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False, index=True)
    stock = Column(Integer, nullable=False, default=0)
    sku = Column(String(50), nullable=True, unique=True, index=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Внешние ключи
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id", ondelete="SET NULL"), nullable=True, index=True)

    # Отношения
    category = relationship("Category", backref="products")
    brand = relationship("Brand", backref="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product {self.name}>"
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from models.base import BaseModel


class ProductImage(BaseModel):
    """
    Модель для изображений товаров
    """
    __tablename__ = "product_images"

    image_url = Column(String(255), nullable=False)
    alt_text = Column(String(255), nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)

    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)

    # Отношение
    product = relationship("Product", back_populates="images")

    def __repr__(self):
        return f"<ProductImage {self.image_url}>"
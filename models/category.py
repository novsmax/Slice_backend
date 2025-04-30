from sqlalchemy import Column, String, Text
from models.base import BaseModel


class Category(BaseModel):
    """
    Модель для категорий товаров
    """
    __tablename__ = "categories"

    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Category {self.name}>"
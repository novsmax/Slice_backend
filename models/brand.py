from sqlalchemy import Column, String, Text
from models.base import BaseModel


class Brand(BaseModel):
    """
    Модель для брендов товаров
    """
    __tablename__ = "brands"

    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    logo_url = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<Brand {self.name}>"
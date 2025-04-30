from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from database import Base


class BaseModel(Base):
    """
    Базовая модель с общими полями для всех таблиц
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
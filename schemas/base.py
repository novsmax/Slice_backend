from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Generic, TypeVar, List, Dict, Any

T = TypeVar('T')


class BaseSchema(BaseModel):

    class Config:
        orm_mode = True
        populate_by_name = True


class IDSchema(BaseSchema):
    """Схема для объектов с ID"""
    id: int


class TimestampSchema(BaseSchema):
    """Схема для объектов с временными метками"""
    created_at: datetime
    updated_at: datetime


class PaginationParams(BaseSchema):
    """Параметры пагинации для запросов"""
    page: int = Field(1, description="Номер страницы (начиная с 1)", ge=1)
    per_page: int = Field(20, description="Количество элементов на странице", ge=1, le=100)


class SearchParams(BaseSchema):
    query: str = Field("", description="Поисковый запрос")


class PaginatedResponse(BaseSchema, Generic[T]):
    """Обертка для пагинированного ответа"""
    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int
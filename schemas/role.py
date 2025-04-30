from pydantic import BaseModel, Field
from typing import Optional
from schemas.base import BaseSchema, IDSchema, TimestampSchema


class RoleBase(BaseSchema):
    """Базовые поля роли"""
    name: str = Field(..., min_length=1, max_length=50, description="Название роли")
    description: Optional[str] = Field(None, max_length=255, description="Описание роли")
    can_read: bool = Field(True, description="Право на чтение данных")
    can_create: bool = Field(False, description="Право на создание данных")
    can_update: bool = Field(False, description="Право на обновление данных")
    can_delete: bool = Field(False, description="Право на удаление данных")
    is_admin: bool = Field(False, description="Права администратора")


class RoleCreate(RoleBase):
    """Схема для создания роли"""
    pass


class RoleUpdate(BaseSchema):
    """Схема для обновления роли"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Название роли")
    description: Optional[str] = Field(None, max_length=255, description="Описание роли")
    can_read: Optional[bool] = Field(None, description="Право на чтение данных")
    can_create: Optional[bool] = Field(None, description="Право на создание данных")
    can_update: Optional[bool] = Field(None, description="Право на обновление данных")
    can_delete: Optional[bool] = Field(None, description="Право на удаление данных")
    is_admin: Optional[bool] = Field(None, description="Права администратора")


class RoleInDB(RoleBase, IDSchema, TimestampSchema):
    """Полная схема роли из БД"""
    pass


class Role(RoleInDB):
    """Схема для возвращения роли в API"""
    pass
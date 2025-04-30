from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime
from schemas.base import BaseSchema, IDSchema, TimestampSchema
from schemas.role import Role


class UserBase(BaseSchema):
    """Базовые поля пользователя"""
    email: EmailStr = Field(..., description="Email пользователя")
    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    full_name: Optional[str] = Field(None, max_length=100, description="Полное имя пользователя")
    is_active: bool = Field(True, description="Активен ли пользователь")
    role_id: int = Field(..., description="ID роли пользователя")


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    password: str = Field(..., min_length=8, max_length=100, description="Пароль пользователя")

    @validator('password')
    def password_strength(cls, v):
        """Проверка сложности пароля"""
        if len(v) < 8:
            raise ValueError('Пароль должен содержать не менее 8 символов')
        if not any(c.isupper() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        if not any(c.islower() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну строчную букву')
        if not any(c.isdigit() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        return v


class UserUpdate(BaseSchema):
    """Схема для обновления пользователя"""
    email: Optional[EmailStr] = Field(None, description="Email пользователя")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Имя пользователя")
    full_name: Optional[str] = Field(None, max_length=100, description="Полное имя пользователя")
    is_active: Optional[bool] = Field(None, description="Активен ли пользователь")
    role_id: Optional[int] = Field(None, description="ID роли пользователя")
    password: Optional[str] = Field(None, min_length=8, max_length=100, description="Новый пароль пользователя")

    @validator('password')
    def password_strength(cls, v):
        """Проверка сложности пароля"""
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError('Пароль должен содержать не менее 8 символов')
        if not any(c.isupper() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        if not any(c.islower() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну строчную букву')
        if not any(c.isdigit() for c in v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        return v


class UserInDB(UserBase, IDSchema, TimestampSchema):
    """Полная схема пользователя из БД"""
    hashed_password: str
    last_login: Optional[datetime] = None


class User(BaseSchema):
    """Схема для возвращения информации о пользователе в API"""
    id: int
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool
    role_id: int
    created_at: datetime
    last_login: Optional[datetime] = None


class UserWithRole(User):
    """Схема для возвращения информации о пользователе с данными о его роли"""
    role: Role


# Схемы для аутентификации
class Token(BaseSchema):
    """Схема для JWT токена"""
    access_token: str
    token_type: str = "bearer"
    user: User


class TokenData(BaseSchema):
    """Схема данных из токена"""
    sub: Optional[str] = None
    exp: Optional[datetime] = None
    role_id: Optional[int] = None
    is_admin: Optional[bool] = None
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from models.base import BaseModel


class User(BaseModel):
    """
    Модель пользователя
    """
    __tablename__ = "users"

    email = Column(String(320), nullable=False, unique=True, index=True)
    username = Column(String(50), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    role = relationship("Role", backref="users")
    last_login = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<User {self.username}>"
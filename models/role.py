from sqlalchemy import Column, String, Integer, Boolean
from models.base import BaseModel


class Role(BaseModel):
    """
    Модель роли пользователя
    """
    __tablename__ = "roles"

    name = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=True)

    can_read = Column(Boolean, default=True, nullable=False)
    can_create = Column(Boolean, default=False, nullable=False)
    can_update = Column(Boolean, default=False, nullable=False)
    can_delete = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<Role {self.name}>"
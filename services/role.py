from typing import List, Optional
from sqlalchemy.orm import Session

from models.role import Role
from schemas.role import RoleCreate, RoleUpdate
from services.base import BaseService


class RoleService(BaseService[Role, RoleCreate, RoleUpdate]):
    """
    Сервис для работы с ролями пользователей
    """

    def __init__(self):
        super().__init__(Role)

    def get_by_name(self, db: Session, name: str) -> Optional[Role]:
        """
        Получение роли по названию

        Args:
            db: Сессия базы данных
            name: Название роли

        Returns:
            Объект роли или None, если не найден
        """
        return db.query(Role).filter(Role.name == name).first()
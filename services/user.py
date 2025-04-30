from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from models.user import User
from schemas.user import UserCreate, UserUpdate
from services.base import BaseService
from utils.auth import get_password_hash, verify_password


class UserService(BaseService[User, UserCreate, UserUpdate]):
    """
    Сервис для работы с пользователями
    """

    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Получение пользователя по email

        Args:
            db: Сессия базы данных
            email: Email пользователя

        Returns:
            Объект пользователя или None, если не найден
        """
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        Получение пользователя по имени пользователя

        Args:
            db: Сессия базы данных
            username: Имя пользователя

        Returns:
            Объект пользователя или None, если не найден
        """
        return db.query(User).filter(User.username == username).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Создание нового пользователя с хешированным паролем

        Args:
            db: Сессия базы данных
            obj_in: Данные для создания пользователя

        Returns:
            Созданный объект пользователя
        """
        hashed_password = get_password_hash(obj_in.password)
        obj_data = obj_in.dict(exclude={"password"})

        db_obj = User(
            **obj_data,
            hashed_password=hashed_password
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        """
        Обновление данных пользователя

        Args:
            db: Сессия базы данных
            db_obj: Объект пользователя для обновления
            obj_in: Данные для обновления пользователя

        Returns:
            Обновленный объект пользователя
        """
        # Получаем словарь из данных схемы
        update_data = obj_in.dict(exclude_unset=True)

        # Если есть новый пароль, хешируем его
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[User]:
        """
        Аутентификация пользователя по имени пользователя и паролю

        Args:
            db: Сессия базы данных
            username: Имя пользователя
            password: Пароль

        Returns:
            Объект пользователя или None, если аутентификация не удалась
        """
        user = self.get_by_username(db, username=username)
        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    def update_last_login(self, db: Session, *, user: User) -> User:
        """
        Обновление времени последнего входа пользователя

        Args:
            db: Сессия базы данных
            user: Объект пользователя

        Returns:
            Обновленный объект пользователя
        """
        user.last_login = datetime.utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)

        return user
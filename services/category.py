from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models.category import Category
from schemas.category import CategoryCreate, CategoryUpdate
from services.base import BaseService


class CategoryService(BaseService[Category, CategoryCreate, CategoryUpdate]):
    """
    Сервис для работы с категориями товаров
    """

    def __init__(self):
        super().__init__(Category)

    def get_by_name(self, db: Session, name: str) -> Optional[Category]:
        """
        Получение категории по названию

        Args:
            db: Сессия базы данных
            name: Название категории

        Returns:
            Объект категории или None, если не найден
        """
        return db.query(Category).filter(Category.name == name).first()

    def search(
            self,
            db: Session,
            *,
            query: str,
            skip: int = 0,
            limit: int = 100
    ) -> List[Category]:
        """
        Поиск категорий по названию или описанию

        Args:
            db: Сессия базы данных
            query: Поисковый запрос
            skip: Количество пропускаемых записей
            limit: Максимальное количество возвращаемых записей

        Returns:
            Список объектов категорий
        """
        search_term = f"%{query}%"
        return db.query(Category).filter(
            or_(
                Category.name.ilike(search_term),
                Category.description.ilike(search_term)
            )
        ).offset(skip).limit(limit).all()

    def search_count(self, db: Session, *, query: str) -> int:
        """
        Подсчет количества категорий, соответствующих поисковому запросу

        Args:
            db: Сессия базы данных
            query: Поисковый запрос

        Returns:
            Количество категорий
        """
        search_term = f"%{query}%"
        return db.query(Category).filter(
            or_(
                Category.name.ilike(search_term),
                Category.description.ilike(search_term)
            )
        ).count()
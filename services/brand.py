from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models.brand import Brand
from schemas.brand import BrandCreate, BrandUpdate
from services.base import BaseService


class BrandService(BaseService[Brand, BrandCreate, BrandUpdate]):
    """
    Сервис для работы с брендами товаров
    """

    def __init__(self):
        super().__init__(Brand)

    def get_by_name(self, db: Session, name: str) -> Optional[Brand]:
        """
        Получение бренда по названию

        Args:
            db: Сессия базы данных
            name: Название бренда

        Returns:
            Объект бренда или None, если не найден
        """
        return db.query(Brand).filter(Brand.name == name).first()

    def search(
            self,
            db: Session,
            *,
            query: str,
            skip: int = 0,
            limit: int = 100
    ) -> List[Brand]:
        """
        Поиск брендов по названию или описанию

        Args:
            db: Сессия базы данных
            query: Поисковый запрос
            skip: Количество пропускаемых записей
            limit: Максимальное количество возвращаемых записей

        Returns:
            Список объектов брендов
        """
        search_term = f"%{query}%"
        return db.query(Brand).filter(
            or_(
                Brand.name.ilike(search_term),
                Brand.description.ilike(search_term)
            )
        ).offset(skip).limit(limit).all()

    def search_count(self, db: Session, *, query: str) -> int:
        """
        Подсчет количества брендов, соответствующих поисковому запросу

        Args:
            db: Сессия базы данных
            query: Поисковый запрос

        Returns:
            Количество брендов
        """
        search_term = f"%{query}%"
        return db.query(Brand).filter(
            or_(
                Brand.name.ilike(search_term),
                Brand.description.ilike(search_term)
            )
        ).count()
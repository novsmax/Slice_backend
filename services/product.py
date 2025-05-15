from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from models.product import Product
from schemas.product import ProductCreate, ProductUpdate
from services.base import BaseService


class ProductService(BaseService[Product, ProductCreate, ProductUpdate]):
    """
    Сервис для работы с товарами
    """

    def __init__(self):
        super().__init__(Product)

    def get_with_relations(self, db: Session, id: int) -> Optional[Product]:
        """
        Получение товара по ID с загрузкой связанных объектов

        Args:
            db: Сессия базы данных
            id: Идентификатор товара

        Returns:
            Объект товара со связанными объектами или None, если не найден
        """
        return db.query(Product).options(
            joinedload(Product.category),
            joinedload(Product.brand),
            joinedload(Product.images)
        ).filter(Product.id == id).first()

    def get_by_sku(self, db: Session, sku: str) -> Optional[Product]:
        """
        Получение товара по артикулу (SKU)

        Args:
            db: Сессия базы данных
            sku: Артикул товара

        Returns:
            Объект товара или None, если не найден
        """
        return db.query(Product).filter(Product.sku == sku).first()

    def get_multi_with_relations(
            self,
            db: Session,
            *,
            skip: int = 0,
            limit: int = 100,
            filters: Optional[Dict[str, Any]] = None
    ) -> List[Product]:
        """
        Получение списка товаров с загрузкой связанных объектов

        Args:
            db: Сессия базы данных
            skip: Количество пропускаемых записей
            limit: Максимальное количество возвращаемых записей
            filters: Словарь с фильтрами {поле: значение}

        Returns:
            Список объектов товаров со связанными объектами
        """
        query = db.query(Product).options(
            joinedload(Product.category),
            joinedload(Product.brand),
            joinedload(Product.images)
        )

        if filters:
            for field, value in filters.items():
                if hasattr(Product, field) and value is not None:
                    query = query.filter(getattr(Product, field) == value)

        return query.offset(skip).limit(limit).all()

    def search(
        self,
        db: Session,
        *,
        query: str,
        category_id: Optional[int] = None,
        brand_id: Optional[int] = None,
        is_active: Optional[bool] = None,  # Добавляем параметр is_active
        skip: int = 0,
        limit: int = 100,
        with_relations: bool = False
    ) -> List[Product]:
        """
        Поиск товаров по названию, описанию или SKU с возможностью фильтрации по активности
        """
        search_term = f"%{query}%"

        base_query = db.query(Product)

        if with_relations:
            base_query = base_query.options(
                joinedload(Product.category),
                joinedload(Product.brand),
                joinedload(Product.images)
            )

        filters = [
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
                Product.sku.ilike(search_term)
            )
        ]

        if category_id is not None:
            filters.append(Product.category_id == category_id)

        if brand_id is not None:
            filters.append(Product.brand_id == brand_id)
            
        # Добавляем фильтр по активности, если он указан
        if is_active is not None:
            filters.append(Product.is_active == is_active)

        return base_query.filter(*filters).offset(skip).limit(limit).all()

    def search_count(
            self,
            db: Session,
            *,
            query: str,
            category_id: Optional[int] = None,
            brand_id: Optional[int] = None,
            is_active: Optional[bool] = None  # Добавляем параметр is_active
    ) -> int:
        """
        Подсчет количества товаров, соответствующих поисковому запросу
        """
        search_term = f"%{query}%"

        filters = [
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
                Product.sku.ilike(search_term)
            )
        ]

        if category_id is not None:
            filters.append(Product.category_id == category_id)

        if brand_id is not None:
            filters.append(Product.brand_id == brand_id)
            
        # Добавляем фильтр по активности, если он указан
        if is_active is not None:
            filters.append(Product.is_active == is_active)

        return db.query(Product).filter(*filters).count()
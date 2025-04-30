from typing import Generic, TypeVar, Type, List, Optional, Any, Dict, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Базовый класс сервиса для CRUD операций
    """

    def __init__(self, model: Type[ModelType]):
        """
        Инициализация сервиса.

        Args:
            model: SQLAlchemy модель
        """
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """
        Получение записи по ID

        Args:
            db: Сессия базы данных
            id: Идентификатор записи

        Returns:
            Объект модели или None, если не найден
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
            self,
            db: Session,
            *,
            skip: int = 0,
            limit: int = 100,
            filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """
        Получение списка записей с пагинацией и фильтрацией

        Args:
            db: Сессия базы данных
            skip: Количество пропускаемых записей
            limit: Максимальное количество возвращаемых записей
            filters: Словарь с фильтрами {поле: значение}

        Returns:
            Список объектов модели
        """
        query = db.query(self.model)

        # Применяем фильтры, если они есть
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.filter(getattr(self.model, field) == value)

        return query.offset(skip).limit(limit).all()

    def get_count(
            self,
            db: Session,
            filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Получение общего количества записей с учетом фильтров

        Args:
            db: Сессия базы данных
            filters: Словарь с фильтрами {поле: значение}

        Returns:
            Количество записей
        """
        query = select(func.count()).select_from(self.model)

        # Применяем фильтры, если они есть
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)

        return db.scalar(query)

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Создание новой записи

        Args:
            db: Сессия базы данных
            obj_in: Схема данных для создания

        Returns:
            Созданный объект модели
        """
        obj_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
            self,
            db: Session,
            *,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Обновление существующей записи

        Args:
            db: Сессия базы данных
            db_obj: Объект модели для обновления
            obj_in: Схема данных для обновления или словарь с полями

        Returns:
            Обновленный объект модели
        """
        obj_data = jsonable_encoder(db_obj)

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Optional[ModelType]:
        """
        Удаление записи по ID

        Args:
            db: Сессия базы данных
            id: Идентификатор записи

        Returns:
            Удаленный объект модели или None, если запись не найдена
        """
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
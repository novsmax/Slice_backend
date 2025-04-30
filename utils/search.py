from typing import List, Dict, Any, Optional, Type, TypeVar, Generic
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session, Query

from database import Base

ModelType = TypeVar("ModelType", bound=Base)


class SearchEngine(Generic[ModelType]):

    def __init__(
            self,
            model: Type[ModelType],
            search_fields: List[str],
            filter_fields: Optional[Dict[str, str]] = None
    ):

        self.model = model
        self.search_fields = search_fields
        self.filter_fields = filter_fields or {}

    def create_base_query(self, db: Session) -> Query:

        return db.query(self.model)

    def apply_search(self, query: Query, search_term: str) -> Query:

        if not search_term:
            return query

        search_conditions = []
        like_term = f"%{search_term}%"

        for field_name in self.search_fields:
            if hasattr(self.model, field_name):
                field = getattr(self.model, field_name)
                search_conditions.append(field.ilike(like_term))

        if search_conditions:
            return query.filter(or_(*search_conditions))

        return query

    def apply_filters(self, query: Query, filters: Dict[str, Any]) -> Query:

        if not filters:
            return query

        filter_conditions = []

        for filter_name, value in filters.items():
            if value is None:
                continue

            field_name = self.filter_fields.get(filter_name, filter_name)

            if hasattr(self.model, field_name):
                field = getattr(self.model, field_name)
                filter_conditions.append(field == value)

        if filter_conditions:
            return query.filter(and_(*filter_conditions))

        return query

    def search(
            self,
            db: Session,
            query: Optional[str] = None,
            filters: Optional[Dict[str, Any]] = None,
            skip: int = 0,
            limit: int = 100,
            query_modifiers: Optional[List] = None
    ) -> List[ModelType]:

        db_query = self.create_base_query(db)

        if query:
            db_query = self.apply_search(db_query, query)

        if filters:
            db_query = self.apply_filters(db_query, filters)

        if query_modifiers:
            for modifier in query_modifiers:
                db_query = modifier(db_query)

        return db_query.offset(skip).limit(limit).all()

    def count(
            self,
            db: Session,
            query: Optional[str] = None,
            filters: Optional[Dict[str, Any]] = None
    ) -> int:

        db_query = self.create_base_query(db)

        if query:
            db_query = self.apply_search(db_query, query)

        if filters:
            db_query = self.apply_filters(db_query, filters)

        return db_query.count()
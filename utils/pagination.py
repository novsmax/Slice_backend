from typing import TypeVar, Generic, List, Optional, Dict, Any, Type, Callable
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from sqlalchemy.sql.elements import BinaryExpression
from pydantic import BaseModel

from database import Base

ModelType = TypeVar("ModelType", bound=Base)
SchemaType = TypeVar("SchemaType", bound=BaseModel)


class Paginator(Generic[ModelType, SchemaType]):


    def __init__(
            self,
            model: Type[ModelType],
            search_fields: Optional[List[str]] = None,
            filter_builders: Optional[Dict[str, Callable[[Any], BinaryExpression]]] = None
    ):

        self.model = model
        self.search_fields = search_fields or []
        self.filter_builders = filter_builders or {}

    def build_search_filters(self, query: str) -> List[BinaryExpression]:

        search_term = f"%{query}%"
        filters = []

        for field_name in self.search_fields:
            if hasattr(self.model, field_name):
                field = getattr(self.model, field_name)
                filters.append(field.ilike(search_term))

        return filters

    def build_filters(self, filters: Dict[str, Any]) -> List[BinaryExpression]:

        result = []

        for field_name, value in filters.items():
            if value is None:
                continue

            if field_name in self.filter_builders:
                filter_expr = self.filter_builders[field_name](value)
                if filter_expr is not None:
                    result.append(filter_expr)
                continue

            if hasattr(self.model, field_name):
                field = getattr(self.model, field_name)
                result.append(field == value)

        return result

    def paginate(
            self,
            db: Session,
            page: int = 1,
            per_page: int = 20,
            filters: Optional[Dict[str, Any]] = None,
            search_query: Optional[str] = None,
            query_modifiers: Optional[List[Callable]] = None,
            include_total: bool = True
    ) -> Dict[str, Any]:

        skip = (page - 1) * per_page

        query = db.query(self.model)

        all_filters = []

        if filters:
            filter_expressions = self.build_filters(filters)
            all_filters.extend(filter_expressions)

        if search_query and self.search_fields:
            search_filters = self.build_search_filters(search_query)
            if search_filters:
                all_filters.append(or_(*search_filters))

        if all_filters:
            query = query.filter(and_(*all_filters))

        if query_modifiers:
            for modifier in query_modifiers:
                query = modifier(query)

        total = None
        if include_total:
            total_query = query.with_entities(func.count())
            total = total_query.scalar()

        items = query.offset(skip).limit(per_page).all()

        pages = None
        if total is not None:
            pages = (total + per_page - 1) // per_page

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages
        }
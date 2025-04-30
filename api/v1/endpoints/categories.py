from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.category import Category
from models.user import User
from schemas.category import Category as CategorySchema, CategoryCreate, CategoryUpdate
from schemas.base import PaginatedResponse
from services.category import CategoryService
from utils.auth import get_current_user, check_create_access, check_update_access, check_delete_access

router = APIRouter()
service = CategoryService()


@router.get("/", response_model=PaginatedResponse[CategorySchema])
def list_categories(
        page: int = Query(1, ge=1, description="Номер страницы"),
        per_page: int = Query(20, ge=1, le=100, description="Количество элементов на странице"),
        query: Optional[str] = Query(None, description="Поисковый запрос"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)  # Требуется авторизация
) -> Any:
    """
    Получение списка категорий с пагинацией и возможностью поиска.
    """
    skip = (page - 1) * per_page

    if query:
        items = service.search(db, query=query, skip=skip, limit=per_page)
        total = service.search_count(db, query=query)
    else:
        items = service.get_multi(db, skip=skip, limit=per_page)
        total = service.get_count(db)

    pages = (total + per_page - 1) // per_page

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages
    }


@router.post("/", response_model=CategorySchema, status_code=201)
def create_category(
        category_in: CategoryCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_create_access)
) -> Any:
    """
    Создание новой категории товаров.
    """
    # Проверяем, существует ли категория с таким названием
    existing_category = service.get_by_name(db, name=category_in.name)
    if existing_category:
        raise HTTPException(
            status_code=400,
            detail=f"Категория с названием '{category_in.name}' уже существует"
        )

    return service.create(db, obj_in=category_in)


@router.get("/{category_id}", response_model=CategorySchema)
def get_category(
        category_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> Any:
    """
    Получение информации о категории по ID.
    """
    category = service.get(db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail=f"Категория с ID {category_id} не найдена"
        )

    return category


@router.put("/{category_id}", response_model=CategorySchema)
def update_category(
        category_id: int,
        category_in: CategoryUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_update_access)
) -> Any:
    """
    Обновление категории товаров по ID.
    """
    category = service.get(db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail=f"Категория с ID {category_id} не найдена"
        )

    if category_in.name and category_in.name != category.name:
        existing_category = service.get_by_name(db, name=category_in.name)
        if existing_category:
            raise HTTPException(
                status_code=400,
                detail=f"Категория с названием '{category_in.name}' уже существует"
            )

    return service.update(db, db_obj=category, obj_in=category_in)


@router.delete("/{category_id}", response_model=CategorySchema)
def delete_category(
        category_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_delete_access)
) -> Any:
    """
    Удаление категории товаров по ID.
    """
    category = service.get(db, id=category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail=f"Категория с ID {category_id} не найдена"
        )

    return service.remove(db, id=category_id)
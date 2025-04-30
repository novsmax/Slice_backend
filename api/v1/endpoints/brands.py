from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.brand import Brand
from models.user import User
from schemas.brand import Brand as BrandSchema, BrandCreate, BrandUpdate
from schemas.base import PaginatedResponse
from services.brand import BrandService
from utils.auth import get_current_user, check_create_access, check_update_access, check_delete_access

router = APIRouter()
service = BrandService()


@router.get("/", response_model=PaginatedResponse[BrandSchema])
def list_brands(
        page: int = Query(1, ge=1, description="Номер страницы"),
        per_page: int = Query(20, ge=1, le=100, description="Количество элементов на странице"),
        query: Optional[str] = Query(None, description="Поисковый запрос"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> Any:
    """
    Получение списка брендов с пагинацией и возможностью поиска.
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


@router.post("/", response_model=BrandSchema, status_code=201)
def create_brand(
        brand_in: BrandCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_create_access)
) -> Any:
    """
    Создание нового бренда товаров.
    """
    existing_brand = service.get_by_name(db, name=brand_in.name)
    if existing_brand:
        raise HTTPException(
            status_code=400,
            detail=f"Бренд с названием '{brand_in.name}' уже существует"
        )

    return service.create(db, obj_in=brand_in)


@router.get("/{brand_id}", response_model=BrandSchema)
def get_brand(
        brand_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> Any:
    """
    Получение информации о бренде по ID.
    """
    brand = service.get(db, id=brand_id)
    if not brand:
        raise HTTPException(
            status_code=404,
            detail=f"Бренд с ID {brand_id} не найден"
        )

    return brand


@router.put("/{brand_id}", response_model=BrandSchema)
def update_brand(
        brand_id: int,
        brand_in: BrandUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_update_access)
) -> Any:
    """
    Обновление бренда товаров по ID.
    """
    brand = service.get(db, id=brand_id)
    if not brand:
        raise HTTPException(
            status_code=404,
            detail=f"Бренд с ID {brand_id} не найден"
        )

    if brand_in.name and brand_in.name != brand.name:
        existing_brand = service.get_by_name(db, name=brand_in.name)
        if existing_brand:
            raise HTTPException(
                status_code=400,
                detail=f"Бренд с названием '{brand_in.name}' уже существует"
            )

    return service.update(db, db_obj=brand, obj_in=brand_in)


@router.delete("/{brand_id}", response_model=BrandSchema)
def delete_brand(
        brand_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_delete_access)
) -> Any:
    """
    Удаление бренда товаров по ID.
    """
    brand = service.get(db, id=brand_id)
    if not brand:
        raise HTTPException(
            status_code=404,
            detail=f"Бренд с ID {brand_id} не найден"
        )

    return service.remove(db, id=brand_id)
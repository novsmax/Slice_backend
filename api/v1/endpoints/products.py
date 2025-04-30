from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.product import Product
from models.user import User
from schemas.product import Product as ProductSchema, ProductDetail, ProductCreate, ProductUpdate
from schemas.base import PaginatedResponse
from services.product import ProductService
from utils.auth import get_current_user, check_create_access, check_update_access, check_delete_access

router = APIRouter()
service = ProductService()


@router.get("/", response_model=PaginatedResponse[ProductSchema])
def list_products(
        page: int = Query(1, ge=1, description="Номер страницы"),
        per_page: int = Query(20, ge=1, le=100, description="Количество элементов на странице"),
        query: Optional[str] = Query(None, description="Поисковый запрос"),
        category_id: Optional[int] = Query(None, description="Фильтр по категории"),
        brand_id: Optional[int] = Query(None, description="Фильтр по бренду"),
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> Any:
    """
    Получение списка товаров с пагинацией, поиском и фильтрацией.
    """
    skip = (page - 1) * per_page

    if query:
        items = service.search(
            db,
            query=query,
            category_id=category_id,
            brand_id=brand_id,
            skip=skip,
            limit=per_page
        )
        total = service.search_count(
            db,
            query=query,
            category_id=category_id,
            brand_id=brand_id
        )
    else:
        filters = {}
        if category_id is not None:
            filters["category_id"] = category_id
        if brand_id is not None:
            filters["brand_id"] = brand_id

        items = service.get_multi(db, skip=skip, limit=per_page, filters=filters)
        total = service.get_count(db, filters=filters)

    pages = (total + per_page - 1) // per_page

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages
    }


@router.post("/", response_model=ProductSchema, status_code=201)
def create_product(
        product_in: ProductCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_create_access)
) -> Any:
    """
    Создание нового товара.
    """
    # Проверяем уникальность SKU, если он указан
    if product_in.sku:
        existing_product = service.get_by_sku(db, sku=product_in.sku)
        if existing_product:
            raise HTTPException(
                status_code=400,
                detail=f"Товар с артикулом '{product_in.sku}' уже существует"
            )

    return service.create(db, obj_in=product_in)


@router.get("/{product_id}", response_model=ProductDetail)
def get_product(
        product_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> Any:
    """
    Получение детальной информации о товаре по ID.
    """
    product = service.get_with_relations(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Товар с ID {product_id} не найден"
        )

    return product


@router.put("/{product_id}", response_model=ProductSchema)
def update_product(
        product_id: int,
        product_in: ProductUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_update_access)
) -> Any:
    """
    Обновление товара по ID.
    """
    product = service.get(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Товар с ID {product_id} не найден"
        )

    # Если SKU меняется, проверяем уникальность
    if product_in.sku and product_in.sku != product.sku:
        existing_product = service.get_by_sku(db, sku=product_in.sku)
        if existing_product:
            raise HTTPException(
                status_code=400,
                detail=f"Товар с артикулом '{product_in.sku}' уже существует"
            )

    return service.update(db, db_obj=product, obj_in=product_in)


@router.delete("/{product_id}", response_model=ProductSchema)
def delete_product(
        product_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_delete_access)
) -> Any:
    """
    Удаление товара по ID.
    """
    product = service.get(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Товар с ID {product_id} не найден"
        )

    return service.remove(db, id=product_id)
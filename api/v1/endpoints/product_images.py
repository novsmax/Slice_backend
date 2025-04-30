from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models.product import Product
from models.product_image import ProductImage
from models.user import User
from schemas.product_image import ProductImage as ProductImageSchema, ProductImageCreate, ProductImageUpdate
from services.product_image import ProductImageService
from services.product import ProductService
from utils.auth import get_current_user, check_create_access, check_update_access, check_delete_access

router = APIRouter()
service = ProductImageService()
product_service = ProductService()


@router.get("/by-product/{product_id}", response_model=List[ProductImageSchema])
def list_product_images(
        product_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> Any:
    """
    Получение списка изображений товара по ID товара.
    """
    # Проверяем, существует ли товар
    product = product_service.get(db, id=product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Товар с ID {product_id} не найден"
        )

    return service.get_by_product(db, product_id=product_id)


@router.post("/", response_model=ProductImageSchema, status_code=201)
def create_product_image(
        image_in: ProductImageCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_create_access)
) -> Any:
    """
    Добавление нового изображения для товара.
    """
    product = product_service.get(db, id=image_in.product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Товар с ID {image_in.product_id} не найден"
        )

    if image_in.is_primary:
        db.query(ProductImage).filter(
            ProductImage.product_id == image_in.product_id,
            ProductImage.is_primary == True
        ).update({"is_primary": False})

    return service.create(db, obj_in=image_in)


@router.get("/{image_id}", response_model=ProductImageSchema)
def get_product_image(
        image_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> Any:
    """
    Получение информации об изображении товара по ID.
    """
    image = service.get(db, id=image_id)
    if not image:
        raise HTTPException(
            status_code=404,
            detail=f"Изображение с ID {image_id} не найдено"
        )

    return image


@router.put("/{image_id}", response_model=ProductImageSchema)
def update_product_image(
        image_id: int,
        image_in: ProductImageUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_update_access)
) -> Any:
    """
    Обновление изображения товара по ID.
    """
    image = service.get(db, id=image_id)
    if not image:
        raise HTTPException(
            status_code=404,
            detail=f"Изображение с ID {image_id} не найдено"
        )

    if image_in.is_primary and image_in.is_primary != image.is_primary:
        db.query(ProductImage).filter(
            ProductImage.product_id == image.product_id,
            ProductImage.id != image_id,
            ProductImage.is_primary == True
        ).update({"is_primary": False})

    return service.update(db, db_obj=image, obj_in=image_in)


@router.put("/{image_id}/set-primary", response_model=ProductImageSchema)
def set_primary_image(
        image_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_update_access)
) -> Any:
    """
    Установка изображения товара как основного.
    """
    image = service.get(db, id=image_id)
    if not image:
        raise HTTPException(
            status_code=404,
            detail=f"Изображение с ID {image_id} не найдено"
        )

    return service.set_primary(db, image_id=image_id, product_id=image.product_id)


@router.delete("/{image_id}", response_model=ProductImageSchema)
def delete_product_image(
        image_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_delete_access)
) -> Any:
    """
    Удаление изображения товара по ID.
    """
    image = service.get(db, id=image_id)
    if not image:
        raise HTTPException(
            status_code=404,
            detail=f"Изображение с ID {image_id} не найдено"
        )

    return service.remove(db, id=image_id)
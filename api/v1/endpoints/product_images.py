# В начало файла добавьте следующий импорт (или обновите существующий):
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, Form
from sqlalchemy.orm import Session

from database import get_db
from models.product import Product
from schemas.product_image import ProductImage as ProductImageSchema  # Pydantic схема
from models.product_image import ProductImage
from models.user import User
from schemas.product_image import ProductImage as ProductImageSchema, ProductImageCreate, ProductImageUpdate
from services.product_image import ProductImageService
from services.product import ProductService
from utils.auth import get_current_user, check_create_access, check_update_access, check_delete_access
from utils.file_handling import save_upload_file  # Убедитесь, что добавили этот файл

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

@router.post("/upload", response_model=ProductImageSchema, status_code=201)
async def upload_product_image(
    file: UploadFile = File(...),
    product_id: int = Form(...),
    alt_text: Optional[str] = Form(None),
    is_primary: str = Form('false'),  # Получаем как строку
    display_order: int = Form(0),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_create_access)
) -> Any:
    """
    Загрузка нового изображения для товара.
    """
    is_primary_bool = is_primary.lower() == 'true'

    # Проверяем существование товара
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=404,
            detail=f"Товар с ID {product_id} не найден"
        )
    
    # Сохраняем файл
    file_url = await save_upload_file(file, f"products/{product_id}")
    if not file_url:
        raise HTTPException(
            status_code=400,
            detail="Не удалось сохранить файл. Проверьте, что это изображение."
        )
    
    # Если изображение должно быть основным, сбрасываем флаг для других изображений
    if is_primary_bool:
        db.query(ProductImage).filter(
            ProductImage.product_id == product_id,
            ProductImage.is_primary == True
        ).update({"is_primary": False})
    
    # Создаем запись в базе данных
    image_data = {
        "product_id": product_id,
        "image_url": file_url,
        "alt_text": alt_text or product.name,
        "is_primary": is_primary_bool,  # Используем преобразованное значение
        "display_order": display_order
    }
    
    db_obj = ProductImage(**image_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    return db_obj
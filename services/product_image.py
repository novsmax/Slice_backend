from typing import List, Optional
from sqlalchemy.orm import Session

from models.product_image import ProductImage
from schemas.product_image import ProductImageCreate, ProductImageUpdate
from services.base import BaseService


class ProductImageService(BaseService[ProductImage, ProductImageCreate, ProductImageUpdate]):
    """
    Сервис для работы с изображениями товаров
    """

    def __init__(self):
        super().__init__(ProductImage)

    def get_by_product(self, db: Session, product_id: int) -> List[ProductImage]:
        """
        Получение всех изображений для товара

        Args:
            db: Сессия базы данных
            product_id: Идентификатор товара

        Returns:
            Список объектов изображений товара
        """
        return db.query(ProductImage).filter(
            ProductImage.product_id == product_id
        ).order_by(ProductImage.display_order).all()

    def set_primary(self, db: Session, image_id: int, product_id: int) -> Optional[ProductImage]:
        """
        Установка изображения как основного для товара

        Args:
            db: Сессия базы данных
            image_id: Идентификатор изображения
            product_id: Идентификатор товара

        Returns:
            Обновленный объект изображения или None, если не найден
        """
        db.query(ProductImage).filter(
            ProductImage.product_id == product_id,
            ProductImage.is_primary == True
        ).update({"is_primary": False})

        image = db.query(ProductImage).filter(
            ProductImage.id == image_id,
            ProductImage.product_id == product_id
        ).first()

        if image:
            image.is_primary = True
            db.add(image)
            db.commit()
            db.refresh(image)

        return image
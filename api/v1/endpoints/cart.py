from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas.order import CartResponse, CartItemAdd, OrderItem, OrderItemUpdate
from services.order import OrderService
from utils.auth import get_current_user

router = APIRouter()
order_service = OrderService()


@router.get("/", response_model=CartResponse)
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Получение текущей корзины пользователя
    """
    cart = order_service.get_cart_with_items(db, current_user.id)
    return cart


@router.post("/items", response_model=OrderItem, status_code=status.HTTP_201_CREATED)
def add_item_to_cart(
    item: CartItemAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Добавление товара в корзину
    """
    try:
        return order_service.add_item_to_cart(db, current_user.id, item)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/items/{item_id}", response_model=OrderItem)
def update_cart_item(
    item_id: int,
    item_data: OrderItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Обновление элемента корзины
    """
    try:
        item = order_service.update_cart_item(db, current_user.id, item_id, item_data)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Элемент корзины с ID {item_id} не найден"
            )
        return item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item_from_cart(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Удаление товара из корзины
    """
    result = order_service.remove_item_from_cart(db, current_user.id, item_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Элемент корзины с ID {item_id} не найден"
        )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Очистка корзины пользователя
    """
    order_service.clear_cart(db, current_user.id)
from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.order import OrderStatus
from schemas.order import Order, OrderCreate, OrderUpdate
from schemas.base import PaginatedResponse
from services.order import OrderService
from utils.auth import get_current_user, check_admin_access

router = APIRouter()
order_service = OrderService()


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Оформление заказа из корзины
    """
    try:
        return order_service.checkout_cart(db, current_user.id, order_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=PaginatedResponse[Order])
def list_user_orders(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Получение списка заказов пользователя
    """
    skip = (page - 1) * per_page
    
    # Получаем заказы пользователя
    orders = order_service.get_user_orders(
        db, 
        user_id=current_user.id, 
        skip=skip, 
        limit=per_page
    )
    
    # Загружаем элементы для каждого заказа
    for order in orders:
        order_with_items = order_service.get_order_with_items(db, order.id)
        order.items = order_with_items.items
    
    # Получаем общее количество заказов пользователя
    total = order_service.get_user_orders_count(db, user_id=current_user.id)
    
    # Вычисляем общее количество страниц
    pages = (total + per_page - 1) // per_page  # Округление вверх
    
    return {
        "items": orders,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages
    }


@router.get("/history", response_model=PaginatedResponse[Order])
def get_order_history(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
    status: Optional[str] = Query(None, description="Фильтр по статусу заказа"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Получение истории заказов пользователя с возможностью фильтрации по статусу
    """
    skip = (page - 1) * per_page
    
    # Получаем заказы пользователя
    orders = order_service.get_user_orders(
        db, 
        user_id=current_user.id, 
        skip=skip, 
        limit=per_page,
        status=status
    )
    
    # Загружаем элементы для каждого заказа
    for order in orders:
        order_with_items = order_service.get_order_with_items(db, order.id)
        order.items = order_with_items.items
    
    # Получаем общее количество заказов пользователя
    total = order_service.get_user_orders_count(
        db, 
        user_id=current_user.id,
        status=status
    )
    
    # Вычисляем общее количество страниц
    pages = (total + per_page - 1) // per_page  # Округление вверх
    
    return {
        "items": orders,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages
    }


@router.get("/{order_id}", response_model=Order)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Получение информации о заказе
    """
    # Для обычных пользователей - только свои заказы
    if not current_user.role.is_admin:
        order = order_service.get_order_with_items(db, order_id, current_user.id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Заказ с ID {order_id} не найден"
            )
        return order
    
    # Для администраторов - любые заказы
    order = order_service.get_order_with_items(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заказ с ID {order_id} не найден"
        )
    
    return order


@router.put("/{order_id}", response_model=Order)
def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Обновление заказа
    """
    # Получаем заказ
    order = None
    
    # Для обычных пользователей - только свои заказы и ограниченные изменения
    if not current_user.role.is_admin:
        order = order_service.get(db, id=order_id)
        if not order or order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Заказ с ID {order_id} не найден"
            )
        
        # Обычные пользователи могут изменять только заказы в статусе NEW
        # и только адрес, телефон и примечания
        if order.status != OrderStatus.NEW.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нельзя изменить заказ, который уже в обработке или завершен"
            )
        
        # Создаем копию схемы только с разрешенными полями
        allowed_data = OrderUpdate(
            shipping_address=order_data.shipping_address,
            phone_number=order_data.phone_number,
            notes=order_data.notes
        )
        
        updated_order = order_service.update(db, db_obj=order, obj_in=allowed_data)
    else:
        # Администраторы могут изменять любые заказы и все поля
        order = order_service.get(db, id=order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Заказ с ID {order_id} не найден"
            )
        
        if order_data.status:
            try:
                updated_order = order_service.change_order_status(
                    db, order_id, order_data.status.value, admin_only=False
                )
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
            
            order_data_dict = order_data.dict(exclude_unset=True)
            if "status" in order_data_dict:
                del order_data_dict["status"]
            
            # Обновляем остальные поля, если они есть
            if order_data_dict:
                updated_order = order_service.update(db, db_obj=updated_order, obj_in=order_data_dict)
        else:
            updated_order = order_service.update(db, db_obj=order, obj_in=order_data)
    
    # Загружаем элементы заказа
    updated_order = order_service.get_order_with_items(db, updated_order.id)
    
    return updated_order


@router.post("/{order_id}/cancel", response_model=Order)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Отмена заказа и возврат товаров на склад
    """
    try:
        # Для обычных пользователей - только свои заказы и только в статусе NEW
        if not current_user.role.is_admin:
            order = order_service.get(db, id=order_id)
            if not order or order.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Заказ с ID {order_id} не найден"
                )
            
            # Обычные пользователи могут отменять только заказы в статусе NEW
            if order.status != OrderStatus.NEW.value:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Нельзя отменить заказ, который уже в обработке или завершен"
                )
                
            canceled_order = order_service.cancel_order(db, order_id, current_user.id)
        else:
            # Администраторы могут отменять любые заказы
            canceled_order = order_service.cancel_order(db, order_id)
            
        if not canceled_order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Заказ с ID {order_id} не найден"
            )
            
        return canceled_order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Административный доступ к заказам
@router.get("/admin/all", response_model=PaginatedResponse[Order])
def list_all_orders(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
    status: Optional[str] = Query(None, description="Фильтр по статусу заказа"),
    user_id: Optional[int] = Query(None, description="Фильтр по ID пользователя"),
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_access)  # Только администраторы
) -> Any:
    """
    Получение списка всех заказов (только для администраторов)
    """
    skip = (page - 1) * per_page
    
    # Получаем заказы
    orders = order_service.get_admin_orders(
        db, 
        skip=skip, 
        limit=per_page,
        status=status,
        user_id=user_id
    )
    
    # Загружаем элементы для каждого заказа
    for order in orders:
        order_with_items = order_service.get_order_with_items(db, order.id)
        order.items = order_with_items.items
    
    # Получаем общее количество заказов
    total = order_service.get_admin_orders_count(
        db,
        status=status,
        user_id=user_id
    )
    
    # Вычисляем общее количество страниц
    pages = (total + per_page - 1) // per_page  # Округление вверх
    
    return {
        "items": orders,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages
    }


@router.post("/admin/{order_id}/status", response_model=Order)
def change_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_admin_access)  # Только администраторы
) -> Any:
    """
    Изменение статуса заказа (только для администраторов)
    """
    try:
        order = order_service.change_order_status(db, order_id, status)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Заказ с ID {order_id} не найден"
            )
        
        # Загружаем элементы заказа
        order = order_service.get_order_with_items(db, order.id)
        
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
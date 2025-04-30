from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from datetime import datetime

from models.order import Order, OrderStatus
from models.order_item import OrderItem
from models.product import Product
from models.user import User
from schemas.order import OrderCreate, OrderUpdate, CartItemAdd, OrderItemUpdate
from services.base import BaseService


class OrderService(BaseService[Order, OrderCreate, OrderUpdate]):
    def __init__(self):
        super().__init__(Order)
    
    def get_cart(self, db: Session, user_id: int) -> Optional[Order]:
        """
        Получение текущей корзины пользователя или создание новой, если корзины нет
        """
        cart = db.query(Order).filter(
            Order.user_id == user_id,
            Order.status == OrderStatus.CART.value
        ).first()
        
        if not cart:
            cart = Order(
                user_id=user_id,
                status=OrderStatus.CART.value,
                total_amount=0.0
            )
            db.add(cart)
            db.commit()
            db.refresh(cart)
        
        return cart
    
    def get_cart_with_items(self, db: Session, user_id: int) -> Optional[Order]:
        # Получаем корзину
        cart = self.get_cart(db, user_id)
        
        # Загружаем элементы корзины
        db.refresh(cart)
        cart = db.query(Order).options(
            joinedload(Order.items)
        ).filter(Order.id == cart.id).first()
        
        return cart
    
    def add_item_to_cart(
        self,
        db: Session,
        user_id: int,
        item_data: CartItemAdd
    ) -> OrderItem:
        # Получаем корзину
        cart = self.get_cart(db, user_id)
        
        # Проверяем, существует ли товар
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise ValueError(f"Товар с ID {item_data.product_id} не найден")
        
        # Проверяем, достаточно ли товара на складе
        if product.stock < item_data.quantity:
            raise ValueError(f"Недостаточное количество товара на складе. Доступно: {product.stock}")
        
        # Проверяем, есть ли уже такой товар в корзине
        existing_item = db.query(OrderItem).filter(
            OrderItem.order_id == cart.id,
            OrderItem.product_id == item_data.product_id
        ).first()
        
        if existing_item:
            existing_item.quantity += item_data.quantity
            db.add(existing_item)
            item = existing_item
        else:
            # Если товара нет в корзине, создаем новый элемент
            item = OrderItem(
                order_id=cart.id,
                product_id=product.id,
                quantity=item_data.quantity,
                price=product.price,
                product_name=product.name
            )
            db.add(item)
        
        self.recalculate_cart_total(db, cart)
        
        db.commit()
        db.refresh(item)
        
        return item
    
    def update_cart_item(
        self,
        db: Session,
        user_id: int,
        item_id: int,
        item_data: OrderItemUpdate
    ) -> Optional[OrderItem]:
        # Получаем корзину
        cart = self.get_cart(db, user_id)
        
        # Получаем элемент корзины
        item = db.query(OrderItem).filter(
            OrderItem.id == item_id,
            OrderItem.order_id == cart.id
        ).first()
        
        if not item:
            return None
        
        # Проверяем, достаточно ли товара на складе
        if item.product_id and item_data.quantity:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product and product.stock < item_data.quantity:
                raise ValueError(f"Недостаточное количество товара на складе. Доступно: {product.stock}")
        
        # Обновляем элемент
        if item_data.quantity:
            item.quantity = item_data.quantity
            
        db.add(item)
        
        # Обновляем общую сумму корзины
        self.recalculate_cart_total(db, cart)
        
        db.commit()
        db.refresh(item)
        
        return item
    
    def remove_item_from_cart(
        self,
        db: Session,
        user_id: int,
        item_id: int
    ) -> bool:
        # Получаем корзину
        cart = self.get_cart(db, user_id)
        
        # Получаем элемент корзины
        item = db.query(OrderItem).filter(
            OrderItem.id == item_id,
            OrderItem.order_id == cart.id
        ).first()
        
        if not item:
            return False
        
        # Удаляем элемент
        db.delete(item)
        
        # Обновляем общую сумму корзины
        self.recalculate_cart_total(db, cart)
        
        db.commit()
        
        return True
    
    def clear_cart(self, db: Session, user_id: int) -> bool:
        # Получаем корзину
        cart = self.get_cart(db, user_id)
        
        # Удаляем все элементы корзины
        db.query(OrderItem).filter(OrderItem.order_id == cart.id).delete()
        
        # Обновляем общую сумму корзины
        cart.total_amount = 0.0
        db.add(cart)
        
        db.commit()
        
        return True
    
    def checkout_cart(
        self,
        db: Session,
        user_id: int,
        order_data: OrderCreate
    ) -> Optional[Order]:
        # Получаем корзину с элементами
        cart = self.get_cart_with_items(db, user_id)
        
        # Проверяем, есть ли товары в корзине
        if not cart.items:
            raise ValueError("Корзина пуста, нельзя оформить заказ")
        
        # Проверяем наличие товаров на складе
        for item in cart.items:
            if item.product_id:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                if product and product.stock < item.quantity:
                    raise ValueError(f"Недостаточное количество товара '{item.product_name}' на складе. "
                                    f"Доступно: {product.stock}, запрошено: {item.quantity}")
        
        # Обновляем корзину, превращая ее в заказ
        cart.status = OrderStatus.NEW.value
        cart.shipping_address = order_data.shipping_address
        cart.phone_number = order_data.phone_number
        cart.notes = order_data.notes
        
        # Обновляем количество товаров на складе
        for item in cart.items:
            if item.product_id:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                if product:
                    product.stock -= item.quantity
                    db.add(product)
        
        db.add(cart)
        db.commit()
        db.refresh(cart)
        
        return cart
    
    def get_user_orders(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        include_cart: bool = False,
        status: Optional[str] = None
    ) -> List[Order]:
        
        query = db.query(Order).filter(Order.user_id == user_id)
        
        if not include_cart:
            query = query.filter(Order.status != OrderStatus.CART.value)
        
        if status:
            query = query.filter(Order.status == status)
        
        return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    
    def get_user_orders_count(
        self,
        db: Session,
        user_id: int,
        include_cart: bool = False,
        status: Optional[str] = None
    ) -> int:
        """
        Получение количества заказов пользователя
        """
        query = db.query(Order).filter(Order.user_id == user_id)
        
        if not include_cart:
            query = query.filter(Order.status != OrderStatus.CART.value)
        
        if status:
            query = query.filter(Order.status == status)
        
        return query.count()
    
    def get_order_with_items(self, db: Session, order_id: int, user_id: Optional[int] = None) -> Optional[Order]:
        """
        Получение заказа с загрузкой всех элементов
        """
        query = db.query(Order).options(
            joinedload(Order.items)
        ).filter(Order.id == order_id)
        
        # Если указан ID пользователя, проверяем права доступа
        if user_id is not None:
            query = query.filter(Order.user_id == user_id)
        
        return query.first()
    
    def cancel_order(self, db: Session, order_id: int, user_id: Optional[int] = None) -> Optional[Order]:
        """
        Отмена заказа и возврат товаров на склад
        """
        # Получаем заказ с проверкой прав доступа
        if user_id is not None:
            order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
        else:
            order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            return None
        
        # Проверяем, можно ли отменить заказ
        if order.status == OrderStatus.DELIVERED.value:
            raise ValueError("Нельзя отменить доставленный заказ")
        
        if order.status == OrderStatus.CANCELED.value:
            raise ValueError("Заказ уже отменен")
        
        # Получаем элементы заказа
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        
        # Возвращаем товары на склад
        for item in items:
            if item.product_id is not None:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                if product:
                    product.stock += item.quantity
                    db.add(product)
        
        # Меняем статус заказа
        order.status = OrderStatus.CANCELED.value
        db.add(order)
        
        db.commit()
        db.refresh(order)
        
        return order
    
    def recalculate_cart_total(self, db: Session, cart: Order) -> None:
        """
        Пересчет общей суммы корзины
        """
        # Загружаем все элементы корзины
        items = db.query(OrderItem).filter(OrderItem.order_id == cart.id).all()
        
        # Рассчитываем общую сумму
        total = sum(item.price * item.quantity for item in items)
        
        # Обновляем общую сумму корзины
        cart.total_amount = total
        db.add(cart)
    
    def get_admin_orders(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> List[Order]:
        """
        Получение списка заказов для администратора
        """
        query = db.query(Order).filter(Order.status != OrderStatus.CART.value)
        
        if status:
            query = query.filter(Order.status == status)
        
        if user_id:
            query = query.filter(Order.user_id == user_id)
        
        return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_admin_orders_count(
        self,
        db: Session,
        status: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> int:
        """
        Получение количества заказов для администратора
        """
        query = db.query(Order).filter(Order.status != OrderStatus.CART.value)
        
        if status:
            query = query.filter(Order.status == status)
        
        if user_id:
            query = query.filter(Order.user_id == user_id)
        
        return query.count()
    
    def change_order_status(
        self,
        db: Session,
        order_id: int,
        new_status: str,
        admin_only: bool = True
    ) -> Optional[Order]:
        """
        Изменение статуса заказа
        """
        # Проверяем валидность нового статуса
        if new_status not in [status.value for status in OrderStatus]:
            raise ValueError(f"Недопустимый статус заказа: {new_status}")
        
        # Получаем заказ
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            return None
        
        # Запрещаем менять статус на CART (корзина)
        if new_status == OrderStatus.CART.value:
            raise ValueError("Нельзя изменить статус заказа на 'cart'")
        
        # Запрещаем менять статус с CANCELED
        if order.status == OrderStatus.CANCELED.value and admin_only:
            raise ValueError("Нельзя изменить статус отмененного заказа")
        
        # Если меняем статус на DELIVERED, устанавливаем дату завершения
        if new_status == OrderStatus.DELIVERED.value:
            order.completed_at = datetime.utcnow()
        
        # Обновляем статус заказа
        order.status = new_status
        db.add(order)
        
        db.commit()
        db.refresh(order)
        
        return order
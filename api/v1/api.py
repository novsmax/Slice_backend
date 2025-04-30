from fastapi import APIRouter

from api.v1.endpoints import (
    categories, 
    brands, 
    products, 
    product_images,
    auth,
    users,
    roles,
    cart,      
    orders     
)

api_router = APIRouter()

# Маршруты аутентификации (публичные)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Маршруты управления пользователями и ролями (только для админов)
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])

# Маршруты для работы с данными магазина
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(brands.router, prefix="/brands", tags=["brands"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(product_images.router, prefix="/product-images", tags=["product-images"])

# Маршруты для работы с заказами
api_router.include_router(cart.router, prefix="/cart", tags=["cart"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
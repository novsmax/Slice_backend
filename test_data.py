import os
import sys
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import SessionLocal
from models.category import Category
from models.brand import Brand
from models.product import Product
from models.product_image import ProductImage


def create_test_data(db: Session):
    """
    Создание тестовых данных в базе данных.

    Args:
        db: Сессия базы данных
    """
    print("Начинаем заполнение тестовыми данными...")

    # Создаем категории
    categories = [
        Category(name="Смартфоны", description="Мобильные телефоны и смартфоны"),
        Category(name="Ноутбуки", description="Портативные компьютеры"),
        Category(name="Планшеты", description="Планшетные компьютеры"),
        Category(name="Аксессуары", description="Аксессуары для электроники"),
        Category(name="Умные часы", description="Смарт-часы и фитнес-браслеты"),
        Category(name="Телевизоры", description="Smart TV и стандартные телевизоры"),
        Category(name="Аудиотехника", description="Колонки, наушники и аудиосистемы"),
    ]

    print("Добавляем категории...")
    for category in categories:
        db.add(category)

    db.commit()

    brands = [
        Brand(name="Apple", description="Техника Apple", logo_url="https://example.com/logos/apple.png"),
        Brand(name="Samsung", description="Техника Samsung", logo_url="https://example.com/logos/samsung.png"),
        Brand(name="Xiaomi", description="Техника Xiaomi", logo_url="https://example.com/logos/xiaomi.png"),
        Brand(name="Huawei", description="Техника Huawei", logo_url="https://example.com/logos/huawei.png"),
        Brand(name="Lenovo", description="Техника Lenovo", logo_url="https://example.com/logos/lenovo.png"),
        Brand(name="Sony", description="Техника Sony", logo_url="https://example.com/logos/sony.png"),
        Brand(name="LG", description="Техника LG", logo_url="https://example.com/logos/lg.png"),
        Brand(name="Asus", description="Техника Asus", logo_url="https://example.com/logos/asus.png"),
    ]

    print("Добавляем бренды...")
    for brand in brands:
        db.add(brand)

    db.commit()

    products = [
        Product(
            name="iPhone 15 Pro Max 256GB",
            description="Смартфон Apple iPhone 15 Pro Max с объемом памяти 256GB, процессором A17 Pro и передовой камерой с пятикратным оптическим зумом.",
            price=159990.0,
            stock=10,
            sku="APIP15PM256",
            is_active=True,
            category_id=1,  # Смартфоны
            brand_id=1,  # Apple
        ),
        Product(
            name="Samsung Galaxy S23 Ultra 512GB",
            description="Смартфон Samsung Galaxy S23 Ultra с объемом памяти 512GB, процессором Snapdragon 8 Gen 2 и фирменным S Pen.",
            price=129990.0,
            stock=15,
            sku="SGS23U512",
            is_active=True,
            category_id=1,  # Смартфоны
            brand_id=2,  # Samsung
        ),
        Product(
            name="Xiaomi 13T Pro 256GB",
            description="Смартфон Xiaomi 13T Pro с объемом памяти 256GB, процессором Dimensity 9200+ и камерой Leica.",
            price=69990.0,
            stock=20,
            sku="XIR13TP256",
            is_active=True,
            category_id=1,  # Смартфоны
            brand_id=3,  # Xiaomi
        ),

        # Ноутбуки
        Product(
            name="MacBook Pro 16 M3 Pro",
            description="Ноутбук Apple MacBook Pro 16 с процессором M3 Pro, 16 ГБ объединенной памяти и дисплеем Liquid Retina XDR.",
            price=299990.0,
            stock=5,
            sku="APMB16M3P",
            is_active=True,
            category_id=2,  # Ноутбуки
            brand_id=1,  # Apple
        ),
        Product(
            name="Lenovo ThinkPad X1 Carbon Gen 11",
            description="Ноутбук Lenovo ThinkPad X1 Carbon Gen 11 с процессором Intel Core i7 13-го поколения, 16 ГБ RAM и 1 ТБ SSD.",
            price=159990.0,
            stock=8,
            sku="LTPX1C11",
            is_active=True,
            category_id=2,  # Ноутбуки
            brand_id=5,  # Lenovo
        ),

        # Планшеты
        Product(
            name="iPad Pro 12.9 M2 256GB",
            description="Планшет Apple iPad Pro 12.9 с процессором M2, объемом памяти 256GB и дисплеем Liquid Retina XDR.",
            price=149990.0,
            stock=8,
            sku="APIP12M2256",
            is_active=True,
            category_id=3,  # Планшеты
            brand_id=1,  # Apple
        ),
        Product(
            name="Samsung Galaxy Tab S9 Ultra",
            description="Планшет Samsung Galaxy Tab S9 Ultra с 14.6-дюймовым AMOLED-экраном, процессором Snapdragon 8 Gen 2 и 12 ГБ RAM.",
            price=119990.0,
            stock=6,
            sku="SGTS9U",
            is_active=True,
            category_id=3,  # Планшеты
            brand_id=2,  # Samsung
        ),

        # Аксессуары
        Product(
            name="Apple AirPods Pro 2",
            description="Беспроводные наушники Apple AirPods Pro 2 с активным шумоподавлением и адаптивным эквалайзером.",
            price=24990.0,
            stock=30,
            sku="APAP2",
            is_active=True,
            category_id=4,  # Аксессуары
            brand_id=1,  # Apple
        ),
        Product(
            name="Samsung Galaxy Watch 6 Classic",
            description="Умные часы Samsung Galaxy Watch 6 Classic с безелем, датчиком ЭКГ и измерением артериального давления.",
            price=34990.0,
            stock=12,
            sku="SGWC6",
            is_active=True,
            category_id=5,  # Умные часы
            brand_id=2,  # Samsung
        ),

        # Телевизоры
        Product(
            name="Sony Bravia XR A95L",
            description="OLED-телевизор Sony Bravia XR A95L с диагональю 65 дюймов, процессором XR и технологией QD-OLED.",
            price=349990.0,
            stock=3,
            sku="SNYBRXRA95L",
            is_active=True,
            category_id=6,  # Телевизоры
            brand_id=6,  # Sony
        ),
        Product(
            name="LG OLED evo G3",
            description="OLED-телевизор LG OLED evo G3 с диагональю 65 дюймов, процессором α9 Gen6 и технологией Brightness Booster Max.",
            price=279990.0,
            stock=4,
            sku="LGEORG3",
            is_active=True,
            category_id=6,  # Телевизоры
            brand_id=7,  # LG
        ),

        Product(
            name="Sony WH-1000XM5",
            description="Беспроводные наушники Sony WH-1000XM5 с лучшим в индустрии шумоподавлением и 30 часами автономной работы.",
            price=39990.0,
            stock=15,
            sku="SNYWH1000XM5",
            is_active=True,
            category_id=7,  # Аудиотехника
            brand_id=6,  # Sony
        ),
    ]

    print("Добавляем товары...")
    for product in products:
        db.add(product)

    db.commit()

    product_images = [
        # iPhone 15 Pro Max
        ProductImage(
            image_url="https://example.com/images/iphone15promax_1.jpg",
            alt_text="iPhone 15 Pro Max - вид спереди",
            is_primary=True,
            display_order=1,
            product_id=1,
        ),
        ProductImage(
            image_url="https://example.com/images/iphone15promax_2.jpg",
            alt_text="iPhone 15 Pro Max - вид сзади",
            is_primary=False,
            display_order=2,
            product_id=1,
        ),

        # MacBook Pro
        ProductImage(
            image_url="https://example.com/images/macbookpro16_1.jpg",
            alt_text="MacBook Pro 16 - вид спереди",
            is_primary=True,
            display_order=1,
            product_id=4,
        ),
        ProductImage(
            image_url="https://example.com/images/macbookpro16_2.jpg",
            alt_text="MacBook Pro 16 - вид сбоку",
            is_primary=False,
            display_order=2,
            product_id=4,
        ),

        # Samsung Galaxy S23 Ultra
        ProductImage(
            image_url="https://example.com/images/galaxys23ultra_1.jpg",
            alt_text="Samsung Galaxy S23 Ultra - вид спереди",
            is_primary=True,
            display_order=1,
            product_id=2,
        ),

        # Xiaomi 13T Pro
        ProductImage(
            image_url="https://example.com/images/xiaomi13tpro_1.jpg",
            alt_text="Xiaomi 13T Pro - вид спереди",
            is_primary=True,
            display_order=1,
            product_id=3,
        ),

        # iPad Pro
        ProductImage(
            image_url="https://example.com/images/ipadpro12_1.jpg",
            alt_text="iPad Pro 12.9 - вид спереди",
            is_primary=True,
            display_order=1,
            product_id=6,
        ),

        # Другие товары
        ProductImage(
            image_url="https://example.com/images/airpodspro2_1.jpg",
            alt_text="AirPods Pro 2 в зарядном кейсе",
            is_primary=True,
            display_order=1,
            product_id=8,
        ),

        ProductImage(
            image_url="https://example.com/images/sonybravia_1.jpg",
            alt_text="Sony Bravia XR A95L - вид спереди",
            is_primary=True,
            display_order=1,
            product_id=10,
        ),
    ]

    print("Добавляем изображения товаров...")
    for image in product_images:
        db.add(image)

    db.commit()

    print("Тестовые данные успешно созданы!")
    print(f"Добавлено {len(categories)} категорий")
    print(f"Добавлено {len(brands)} брендов")
    print(f"Добавлено {len(products)} товаров")
    print(f"Добавлено {len(product_images)} изображений")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        create_test_data(db)
    except Exception as e:
        print(f"Ошибка при создании тестовых данных: {e}")
    finally:
        db.close()
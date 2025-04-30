import os
import sys
import traceback
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

env_file = os.path.join(os.path.dirname(__file__), '.env')
DATABASE_URL = None

if os.path.exists(env_file):
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    if key == 'DATABASE_URL':
                        DATABASE_URL = value.strip('"\'')
                        break
    except Exception as e:
        print(f"Ошибка при чтении .env файла: {e}")

if not DATABASE_URL:
    DATABASE_URL = "postgresql://slice_user:password@localhost:5432/slice_db"
    print(f"Используется URL базы данных по умолчанию: {DATABASE_URL}")
else:
    print(f"Используется URL базы данных из .env: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    from models.role import Role
    from models.user import User

    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


    def get_password_hash(password: str) -> str:
        """Генерация хеша пароля."""
        return pwd_context.hash(password)


    def create_default_roles_and_admin(db_session):
        """
        Создание стандартных ролей и пользователя-администратора.

        Args:
            db_session: Сессия базы данных
        """
        admin_role = db_session.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(
                name="admin",
                description="Администратор системы (полный доступ)",
                can_read=True,
                can_create=True,
                can_update=True,
                can_delete=True,
                is_admin=True
            )
            db_session.add(admin_role)
            print("Создана роль: admin")

        manager_role = db_session.query(Role).filter(Role.name == "manager").first()
        if not manager_role:
            manager_role = Role(
                name="manager",
                description="Менеджер (может добавлять, изменять и удалять товары)",
                can_read=True,
                can_create=True,
                can_update=True,
                can_delete=True,
                is_admin=False
            )
            db_session.add(manager_role)
            print("Создана роль: manager")

        user_role = db_session.query(Role).filter(Role.name == "user").first()
        if not user_role:
            user_role = Role(
                name="user",
                description="Обычный пользователь (только чтение)",
                can_read=True,
                can_create=False,
                can_update=False,
                can_delete=False,
                is_admin=False
            )
            db_session.add(user_role)
            print("Создана роль: user")

        db_session.commit()

        admin_user = db_session.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_role = db_session.query(Role).filter(Role.name == "admin").first()

            admin_user = User(
                email="admin@slice.com",
                username="admin",
                full_name="System Administrator",
                hashed_password=get_password_hash("admin"),
                is_active=True,
                role_id=admin_role.id
            )
            db_session.add(admin_user)
            print("Создан пользователь: admin (пароль: admin)")

        manager_user = db_session.query(User).filter(User.username == "manager").first()
        if not manager_user:
            manager_role = db_session.query(Role).filter(Role.name == "manager").first()

            manager_user = User(
                email="manager@slice.com",
                username="manager",
                full_name="Store Manager",
                hashed_password=get_password_hash("Manager123!"),
                is_active=True,
                role_id=manager_role.id
            )
            db_session.add(manager_user)
            print("Создан пользователь: manager (пароль: Manager123!)")

        test_user = db_session.query(User).filter(User.username == "user").first()
        if not test_user:
            user_role = db_session.query(Role).filter(Role.name == "user").first()

            test_user = User(
                email="user@slice.com",
                username="user",
                full_name="Regular User",
                hashed_password=get_password_hash("user"),
                is_active=True,
                role_id=user_role.id
            )
            db_session.add(test_user)
            print("Создан пользователь: user (пароль: user)")

        db_session.commit()

        print("Стандартные роли и пользователи успешно созданы!")
        print("\nВнимание! В реальном проекте необходимо сменить стандартные пароли!")


    if __name__ == "__main__":
        db = SessionLocal()
        try:
            create_default_roles_and_admin(db)
        except Exception as e:
            print(f"Ошибка при создании ролей и пользователей: {e}")
            print("\nПолный стек ошибки:")
            traceback.print_exc()
        finally:
            db.close()

except Exception as e:
    print(f"Критическая ошибка инициализации скрипта: {e}")
    print("\nПолный стек ошибки:")
    traceback.print_exc()
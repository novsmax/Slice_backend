from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User
from models.role import Role

def reset_roles_and_users():
    db = SessionLocal()
    try:
        print("Удаление пользователей...")
        db.query(User).delete()
        
        print("Удаление ролей...")
        db.query(Role).delete()
        
        db.commit()
        print("Роли и пользователи успешно удалены.")
    except Exception as e:
        db.rollback()
        print(f"Ошибка при удалении: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_roles_and_users()
    
    print("\nЗапуск скрипта для создания стандартных ролей и пользователей...")
    import os
    os.system("python create_default_roles.py")
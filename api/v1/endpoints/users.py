from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models.user import User
from models.role import Role
from schemas.user import User as UserSchema, UserCreate, UserUpdate, UserWithRole
from schemas.base import PaginatedResponse
from services.user import UserService
from services.role import RoleService
from utils.auth import get_current_user, check_admin_access

router = APIRouter()
user_service = UserService()
role_service = RoleService()


@router.get("/", response_model=PaginatedResponse[UserWithRole])
def list_users(
        page: int = Query(1, ge=1, description="Номер страницы"),
        per_page: int = Query(20, ge=1, le=100, description="Количество элементов на странице"),
        query: Optional[str] = Query(None, description="Поисковый запрос по имени или email"),
        role_id: Optional[int] = Query(None, description="Фильтр по ID роли"),
        db: Session = Depends(get_db),
        current_user: User = Depends(check_admin_access)
) -> Any:
    """
    Получение списка пользователей (только для администраторов).
    """
    skip = (page - 1) * per_page

    query_obj = db.query(User).options(joinedload(User.role))

    if query:
        search_term = f"%{query}%"
        query_obj = query_obj.filter(
            (User.username.ilike(search_term)) |
            (User.email.ilike(search_term)) |
            (User.full_name.ilike(search_term))
        )

    if role_id is not None:
        query_obj = query_obj.filter(User.role_id == role_id)

    total = query_obj.count()
    items = query_obj.offset(skip).limit(per_page).all()
    pages = (total + per_page - 1) // per_page

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages
    }


@router.post("/", response_model=UserWithRole, status_code=201)
def create_user(
        user_in: UserCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_admin_access)
) -> Any:
    """
    Создание нового пользователя (только для администраторов).
    """
    user = user_service.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{user_in.email}' already exists",
        )

    user = user_service.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with username '{user_in.username}' already exists",
        )

    role = db.query(Role).get(user_in.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {user_in.role_id} not found",
        )

    user = user_service.create(db, obj_in=user_in)
    db.refresh(user)

    return user


@router.get("/{user_id}", response_model=UserWithRole)
def get_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_admin_access)
) -> Any:
    """
    Получение информации о пользователе по ID (только для администраторов).
    """
    user = db.query(User).options(joinedload(User.role)).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    return user


@router.put("/{user_id}", response_model=UserWithRole)
def update_user(
        user_id: int,
        user_in: UserUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_admin_access)
) -> Any:
    """
    Обновление пользователя (только для администраторов).
    """
    user = user_service.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    if user_in.email and user_in.email != user.email:
        existing_user = user_service.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email '{user_in.email}' already exists",
            )

    if user_in.username and user_in.username != user.username:
        existing_user = user_service.get_by_username(db, username=user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with username '{user_in.username}' already exists",
            )

    if user_in.role_id:
        role = db.query(Role).get(user_in.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role with ID {user_in.role_id} not found",
            )

    user = user_service.update(db, db_obj=user, obj_in=user_in)
    db.refresh(user)
    db.refresh(user.role)

    return user


@router.delete("/{user_id}", response_model=UserSchema)
def delete_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_admin_access)
) -> Any:
    """
    Удаление пользователя (только для администраторов).
    """
    user = user_service.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself",
        )

    return user_service.remove(db, id=user_id)
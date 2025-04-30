from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.role import Role
from schemas.role import Role as RoleSchema, RoleCreate, RoleUpdate
from schemas.base import PaginatedResponse
from services.role import RoleService
from utils.auth import check_admin_access

router = APIRouter()
role_service = RoleService()


@router.get("/", response_model=PaginatedResponse[RoleSchema])
def list_roles(
        page: int = Query(1, ge=1, description="Номер страницы"),
        per_page: int = Query(20, ge=1, le=100, description="Количество элементов на странице"),
        db: Session = Depends(get_db),
        current_user: User = Depends(check_admin_access)
) -> Any:
    """
    Получение списка ролей (только для администраторов).
    """
    skip = (page - 1) * per_page
    total = db.query(Role).count()
    items = db.query(Role).offset(skip).limit(per_page).all()
    pages = (total + per_page - 1) // per_page

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages
    }


@router.post("/", response_model=RoleSchema, status_code=201)
def create_role(
        role_in: RoleCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_admin_access)
) -> Any:
    """
    Создание новой роли (только для администраторов).
    """
    role = role_service.get_by_name(db, name=role_in.name)
    if role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with name '{role_in.name}' already exists",
        )

    # Создаем роль
    role = role_service.create(db, obj_in=role_in)

    return role


@router.get("/{role_id}", response_model=RoleSchema)
def get_role(
        role_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_admin_access)
) -> Any:
    """
    Получение информации о роли по ID (только для администраторов).
    """
    role = role_service.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found",
        )

    return role


@router.put("/{role_id}", response_model=RoleSchema)
def update_role(
        role_id: int,
        role_in: RoleUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_admin_access)
) -> Any:
    """
    Обновление роли (только для администраторов).
    """
    role = role_service.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found",
        )

    if role_in.name and role_in.name != role.name:
        existing_role = role_service.get_by_name(db, name=role_in.name)
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role with name '{role_in.name}' already exists",
            )

    role = role_service.update(db, db_obj=role, obj_in=role_in)

    return role


@router.delete("/{role_id}", response_model=RoleSchema)
def delete_role(
        role_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(check_admin_access)
) -> Any:
    """
    Удаление роли (только для администраторов).
    """
    role = role_service.get(db, id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found",
        )

    users_count = db.query(User).filter(User.role_id == role_id).count()
    if users_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete role with ID {role_id} because it is assigned to {users_count} users",
        )

    return role_service.remove(db, id=role_id)
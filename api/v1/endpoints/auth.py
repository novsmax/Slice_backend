from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas.user import Token, User as UserSchema
from services.user import UserService
from utils.auth import create_access_token, get_current_user
from config import get_settings

settings = get_settings()

router = APIRouter()
user_service = UserService()


@router.post("/login", response_model=Token)
def login_for_access_token(
        db: Session = Depends(get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Аутентификация пользователя и выдача JWT токена.
    """
    user = user_service.authenticate(
        db, username=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    user_service.update_last_login(db, user=user)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={
            "sub": user.username,
            "role_id": user.role_id,
            "is_admin": user.role.is_admin
        },
        expires_delta=access_token_expires
    )

    user_data = UserSchema(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        role_id=user.role_id,
        created_at=user.created_at,
        last_login=user.last_login
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }


@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_user)) -> Any:
    return current_user
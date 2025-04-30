from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from schemas.user import TokenData
from config import get_settings

settings = get_settings()

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Настройка OAuth2 с Password Bearer для FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:

    return pwd_context.hash(password)


def create_access_token(
        data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def decode_token(token: str) -> TokenData:

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        exp: datetime = datetime.fromtimestamp(payload.get("exp"))
        role_id: int = payload.get("role_id")
        is_admin: bool = payload.get("is_admin", False)

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return TokenData(sub=username, exp=exp, role_id=role_id, is_admin=is_admin)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
        db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:

    token_data = decode_token(token)
    user = db.query(User).filter(User.username == token_data.sub).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    return user


def check_admin_access(current_user: User = Depends(get_current_user)) -> User:

    if not current_user.role.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return current_user


def check_manager_access(current_user: User = Depends(get_current_user)) -> User:

    if current_user.role.is_admin:
        return current_user

    if not (current_user.role.can_create or current_user.role.can_update or current_user.role.can_delete):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return current_user


def check_create_access(current_user: User = Depends(get_current_user)) -> User:

    if current_user.role.is_admin:
        return current_user

    if not current_user.role.can_create:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create data",
        )

    return current_user


def check_update_access(current_user: User = Depends(get_current_user)) -> User:

    if current_user.role.is_admin:
        return current_user

    if not current_user.role.can_update:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update data",
        )

    return current_user


def check_delete_access(current_user: User = Depends(get_current_user)) -> User:

    if current_user.role.is_admin:
        return current_user

    if not current_user.role.can_delete:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete data",
        )

    return current_user
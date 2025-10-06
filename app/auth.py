from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_async_db
from app.models import User as UserModel


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Хэширует переданный пароль с использованием bcrypt.
    Args:
        password (str): Пароль в виде строки
    Returns:
        str: Хэшированный пароль
    """
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие пароля его хэшу.
    Args:
        password (str): Введённый пароль
        hashed_password (str): Хэш пароля для проверки
    Returns:
        bool: True, если пароль совпадает с хэшем, иначе False
    """
    return pwd_context.verify(password, hashed_password)


def create_access_token(data: dict):
    """
    Создаёт JWT-токен с указанными данными и сроком действия.
    Args:
        data (dict): Словарь с данными для токена (например, email пользователя)
    Returns:
        str: Закодированный JWT-токен
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def authenticate_user(db: AsyncSession, username: str, password: str):
    """
    Аутентифицирует пользователя по email и паролю.
    Args:
        db (AsyncSession): Асинхронная сессия базы данных
        username (str): Email пользователя
        password (str): Пароль пользователя
    Returns:
        UserModel | None: Объект пользователя, если аутентификация успешна, иначе None
    """
    result = await db.execute(select(UserModel).where(UserModel.email == username))
    user = result.scalars().first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_token_from_cookie(request: Request):
    """
    Получает JWT-токен из cookies запроса.
    Args:
        request (Request): Объект запроса FastAPI
    Returns:
        str | None: Токен из cookie или None, если отсутствует
    """
    token = request.cookies.get("access_token")
    return token


async def get_current_user(token: str = Depends(get_token_from_cookie), db: AsyncSession = Depends(get_async_db)):
    """
    Получает текущего авторизованного пользователя по JWT-токену.
    Args:
        token (str): JWT-токен из cookie (зависимость get_token_from_cookie)
        db (AsyncSession): Асинхронная сессия базы данных
    Returns:
        UserModel: Объект текущего пользователя
    """
    if not token:
        raise HTTPException(status_code=401, detail="Не авторизован")
    scheme, _, param = token.partition(" ")
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email: str = payload.get("sub")
    result = await db.scalars(select(UserModel).where(UserModel.email == email))
    user = result.first()
    return user
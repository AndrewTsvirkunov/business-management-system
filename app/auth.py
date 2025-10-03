from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, status, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import SECRET_KEY, ALGORITHM
from app.database import get_async_db
from app.models import User as UserModel


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.PyJWTError:
        raise credentials_exception
    result = await db.scalars(select(UserModel).where(UserModel.email == email))
    user = result.first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_manager(current_user: UserModel = Depends(get_current_user)):
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ только для менеджеров"
        )
    return current_user


async def get_current_user_or_manager(current_user: UserModel = Depends(get_current_user)):
    if current_user.role not in ("user", "manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    return current_user


async def authenticate_user(db: AsyncSession, username: str, password: str):
    result = await db.execute(select(UserModel).where(UserModel.email == username))
    user = result.scalars().first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_token_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    return token


async def get_curr_user(token: str = Depends(get_token_from_cookie), db: AsyncSession = Depends(get_async_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Не авторизован!")
    scheme, _, param = token.partition(" ")
    # if scheme.lower() != "bearer":
    #     raise HTTPException(status_code=401, detail="Неверный токен")
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email: str = payload.get("sub")
    result = await db.scalars(select(UserModel).where(UserModel.email == email))
    user = result.first()
    return user
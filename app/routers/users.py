from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas import UserCreate, UserRead
from app.models import User
from app.database import get_async_db
from app.auth import hash_password, verify_password, create_access_token


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Регистрирует нового пользователя.
    Хэширует пароль, сохраняет пользователя в базе данных и возвращает данные пользователя.
    Args:
        user (UserCreate): Данные нового пользователя
        db (AsyncSession): Асинхронная сессия базы данных
    Returns:
        UserRead: Созданный пользователь.
    """
    db_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role
    )
    db.add(db_user)
    await db.commit()
    return db_user


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_async_db)):
    """
    Аутентифицирует пользователя и возвращает JWT-токен.
    Проверяет email и пароль пользователя. В случае успешной аутентификации
    создаёт токен доступа.
    Args:
        form_data (OAuth2PasswordRequestForm): Данные формы входа (username, password)
        db (AsyncSession): Асинхронная сессия базы данных
    Returns:
        dict: Содержит access_token и тип токена ("bearer")
    """
    result = await db.scalars(select(User).where(User.email == form_data.username))
    user = result.first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = create_access_token({"sub": user.email, "role": user.role, "id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
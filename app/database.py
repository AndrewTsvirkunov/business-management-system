from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from app.config import DATABASE_URL


engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_db() -> AsyncSession:
    """
    Асинхронная зависимость для получения сессии базы данных.
    Используется как Depends в FastAPI эндпоинтах.
    Yields:
        AsyncSession: Асинхронная сессия SQLAlchemy.
    """
    async with async_session() as session:
        yield session


Base = declarative_base()
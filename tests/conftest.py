import pytest_asyncio
import asyncio
import sys
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.database import get_async_db
from app.models import Base, User
from app.main import app
from app.config import TEST_DATABASE_URL


if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False, future=True, poolclass=NullPool)
async_session_test = async_sessionmaker(bind=engine_test, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    """
    Фикстура создает и чистит тестовую БД один раз на сессию.
    """
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def session() -> AsyncSession:
    """
    Фикстура создает сессию для тестовой БД.
    """
    async with async_session_test() as session:
        yield session


@pytest_asyncio.fixture
async def client(session: AsyncSession):
    """
    Асинхронный HTTP клиент для тестирования FastAPI.
    Подменяет зависимость get_async_db на тестовую сессию.
    После завершения теста сбрасывает переопределения зависимостей.
    """
    async def override_get_db():
        async with session.begin():
            yield session

    app.dependency_overrides[get_async_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_user(prepare_database):
    """
    Асинхронная фикстура для создания пользователя с ролью 'admin' в тестовой БД.
    Args:
        prepare_database: фикстура, подготавливающая тестовую базу данных
    Yields:
        User: объект пользователя с ролью 'admin'
    """
    async with async_session_test() as session:
        email = f"admin_{uuid.uuid4().hex}@example.com"
        user = User(name="Admin", email=email, hashed_password="hashed", role="admin")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        yield user


@pytest_asyncio.fixture
async def normal_user(prepare_database):
    """
    Асинхронная фикстура для создания обычного пользователя с ролью 'user' в тестовой БД.
    Args:
        prepare_database: фикстура, подготавливающая тестовую базу данных
    Yields:
        User: объект пользователя с ролью 'user'
    """
    async with async_session_test() as session:
        email = f"admin_{uuid.uuid4().hex}@example.com"
        user = User(name="User", email=email,  hashed_password="hashed", role="user")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        yield user
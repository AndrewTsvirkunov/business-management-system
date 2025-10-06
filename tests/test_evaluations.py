import pytest
from httpx import AsyncClient

from app.main import app
from app.auth import get_current_user


@pytest.mark.asyncio
async def test_evaluations_list(client: AsyncClient, admin_user):
    """
    Тест отображения списка оценок для администратора.
    Проверяет, что страница со списком оценок возвращает статус 200
    и содержит HTML-контент.
    """
    app.dependency_overrides[get_current_user] = lambda: admin_user

    response = await client.get("/evaluations/")
    assert response.status_code == 200
    assert "<html" in response.text

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_evaluation_create_form_admin(client, admin_user):
    """
    Тест формы создания оценки для администратора.
    Проверяет, что администратор может открыть страницу создания оценки
    и получить HTML-контент со статусом 200.
    """
    app.dependency_overrides[get_current_user] = lambda: admin_user

    response = await client.get("/evaluations/create")
    assert response.status_code == 200
    assert "<html" in response.text

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_evaluation_create_form_forbidden(client, normal_user):
    """
    Тест доступа к форме создания оценки для обычного пользователя.
    Проверяет, что пользователь с ролью "user" не может открыть страницу
    создания оценки и получает статус 403 с соответствующим сообщением.
    """
    app.dependency_overrides[get_current_user] = lambda: normal_user

    response = await client.get("/evaluations/create")
    assert response.status_code == 403
    assert "User не может ставить оценки" in response.text

    app.dependency_overrides.clear()
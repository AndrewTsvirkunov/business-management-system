import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_get(client: AsyncClient):
    """
    Тест отображения страницы логина.
    Проверяет, что GET-запрос на /auth/login возвращает статус 200.
    """
    response = await client.get("/auth/login")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_login_post_fail(client: AsyncClient):
    """
    Тест неудачного входа в систему.
    Проверяет, что POST-запрос с неверными учетными данными возвращает HTML с сообщением об ошибке.
    """
    response = await client.post("/auth/login", data={"username": "x", "password": "y"})
    assert response.status_code == 200
    assert "Неверные данные" in response.text


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    """
    Тест выхода пользователя из системы.
    Проверяет, что GET-запрос на /auth/logout возвращает редирект на страницу логина
    со статусом 303 или 307.
    """
    response = await client.get("/auth/logout", follow_redirects=False)
    assert response.status_code in (303, 307)
    assert "/auth/login" in response.headers["location"]

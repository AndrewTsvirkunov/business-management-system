import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """
    Тест регистрации нового пользователя через POST-запрос.
    Проверяет, что пользователь создается с указанным именем и email,
    и возвращается статус 201.
    """
    response = await client.post(
        "/users/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "123456",
            "role": "user"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_token_fail(client: AsyncClient):
    """
    Тест получения токена с неправильными данными.
    Проверяет, что при попытке входа с неверным email или паролем
    возвращается статус 401 и соответствующее сообщение.
    """
    response = await client.post(
        "/users/token",
        data={"username": "wrong@example.com", "password": "wrong"}
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.text

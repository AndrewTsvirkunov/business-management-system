import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_get(client: AsyncClient):
    response = await client.get("/auth/login")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_login_post_fail(client: AsyncClient):
    # неправильные данные — должен вернуть "Неверные данные"
    response = await client.post("/auth/login", data={"username": "x", "password": "y"})
    assert response.status_code == 200
    assert "Неверные данные" in response.text


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    response = await client.get("/auth/logout", follow_redirects=False)
    assert response.status_code in (303, 307)
    assert "/auth/login" in response.headers["location"]

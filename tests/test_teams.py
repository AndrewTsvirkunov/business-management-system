import pytest
from httpx import AsyncClient
from app.main import app
from app.auth import get_current_user


@pytest.mark.asyncio
async def test_teams_list(client: AsyncClient):
    """
    Тест отображения списка команд.
    Проверяет, что GET-запрос на /teams/ возвращает статус 200 и содержит HTML.
    """
    response = await client.get("/teams/")
    assert response.status_code == 200
    assert "<html" in response.text


@pytest.mark.asyncio
async def test_team_create_form_admin(client, admin_user):
    """
    Тест отображения формы создания команды для администратора.
    Проверяет, что GET-запрос на /teams/create возвращает HTML и статус 200.
    """
    app.dependency_overrides[get_current_user] = lambda: admin_user

    response = await client.get("/teams/create")
    assert response.status_code == 200
    assert "<html" in response.text

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_team_create_form_forbidden(client, normal_user):
    """
    Тест запрета создания команды для обычного пользователя.
    Проверяет, что GET-запрос на /teams/create возвращает статус 403 и сообщение о запрете.
    """
    app.dependency_overrides[get_current_user] = lambda: normal_user

    response = await client.get("/teams/create")
    assert response.status_code == 403
    assert "Только admin может создавать команды" in response.text

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_team_create_post(client, admin_user):
    """
    Тест создания команды через POST-запрос.
    Проверяет, что команда создается с указанным названием и возвращается HTML с названием команды.
    """
    app.dependency_overrides[get_current_user] = lambda: admin_user

    response = await client.post(
        "/teams/create",
        data={"title": "Test Team", "user_ids": [admin_user.id]}
    )
    assert response.status_code == 200
    assert "Test Team" in response.text

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_team_edit_form(client, admin_user):
    """
    Тест отображения формы редактирования команды.
    Проверяет, что GET-запрос на /teams/edit/{id} возвращает HTML для администратора.
    """
    app.dependency_overrides[get_current_user] = lambda: admin_user

    await client.post("/teams/create", data={"title": "TeamEdit", "user_ids": [admin_user.id]})
    response = await client.get("/teams/edit/1")
    assert response.status_code == 200

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_team_edit_post(client, admin_user):
    """
    Тест редактирования команды через POST-запрос.
    Проверяет, что изменения сохраняются и возвращается редирект на /teams.
    """
    app.dependency_overrides[get_current_user] = lambda: admin_user

    await client.post("/teams/create", data={"title": "OldTeam", "user_ids": [admin_user.id]})
    response = await client.post("/teams/edit/1", data={"title": "NewTeam", "user_ids": [admin_user.id]})
    assert response.status_code == 303
    assert response.headers["location"] == "/teams"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_team_delete(client, admin_user):
    """
    Тест удаления команды.
    Проверяет, что GET-запрос на /teams/delete/{id} удаляет команду и выполняет редирект на /teams.
    """
    app.dependency_overrides[get_current_user] = lambda: admin_user

    await client.post("/teams/create", data={"title": "TeamToDelete", "user_ids": [admin_user.id]})
    response = await client.get("/teams/delete/1")
    assert response.status_code == 303
    assert response.headers["location"] == "/teams"

    app.dependency_overrides.clear()
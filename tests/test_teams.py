import pytest
from httpx import AsyncClient
from app.main import app
from app.auth import get_current_user


@pytest.mark.asyncio
async def test_teams_list(client: AsyncClient):
    response = await client.get("/teams/")
    assert response.status_code == 200
    assert "<html" in response.text


# ---------------------------
# GET /teams/create — форма создания
# ---------------------------
@pytest.mark.asyncio
async def test_team_create_form_admin(client, admin_user):
    # Подменяем зависимость FastAPI на admin_user
    app.dependency_overrides[get_current_user] = lambda: admin_user

    response = await client.get("/teams/create")
    assert response.status_code == 200
    assert "<html" in response.text

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_team_create_form_forbidden(client, normal_user):
    app.dependency_overrides[get_current_user] = lambda: normal_user

    response = await client.get("/teams/create")
    assert response.status_code == 403
    assert "Только admin может создавать команды" in response.text

    app.dependency_overrides.clear()

# ---------------------------
# POST /teams/create — создание команды
# ---------------------------
@pytest.mark.asyncio
async def test_team_create_post(client, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    response = await client.post(
        "/teams/create",
        data={"title": "Test Team", "user_ids": [admin_user.id]}
    )
    assert response.status_code == 200
    assert "Test Team" in response.text

    app.dependency_overrides.clear()

# ---------------------------
# GET /teams/edit/{team_id} — форма редактирования
# ---------------------------
@pytest.mark.asyncio
async def test_team_edit_form(client, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    # Создаём команду для редактирования
    await client.post("/teams/create", data={"title": "TeamEdit", "user_ids": [admin_user.id]})
    response = await client.get("/teams/edit/1")
    assert response.status_code == 200

    app.dependency_overrides.clear()

# ---------------------------
# POST /teams/edit/{team_id} — редактирование команды
# ---------------------------
@pytest.mark.asyncio
async def test_team_edit_post(client, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    await client.post("/teams/create", data={"title": "OldTeam", "user_ids": [admin_user.id]})
    response = await client.post("/teams/edit/1", data={"title": "NewTeam", "user_ids": [admin_user.id]})
    assert response.status_code == 303
    assert response.headers["location"] == "/teams"

    app.dependency_overrides.clear()

# ---------------------------
# GET /teams/delete/{team_id} — удаление команды
# ---------------------------
@pytest.mark.asyncio
async def test_team_delete(client, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    await client.post("/teams/create", data={"title": "TeamToDelete", "user_ids": [admin_user.id]})
    response = await client.get("/teams/delete/1")
    assert response.status_code == 303
    assert response.headers["location"] == "/teams"

    app.dependency_overrides.clear()
import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from app.main import app
from app.auth import get_current_user


@pytest.mark.asyncio
async def test_meetings_list(client: AsyncClient):
    response = await client.get("/meetings/")
    assert response.status_code == 200
    assert "<html" in response.text


# ---------------------------
# GET /meetings/create — форма создания
# ---------------------------
@pytest.mark.asyncio
async def test_meeting_create_form(client, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    response = await client.get("/meetings/create")
    assert response.status_code == 200
    assert "<html" in response.text

    app.dependency_overrides.clear()


# ---------------------------
# POST /meetings/create — создание встречи
# ---------------------------
@pytest.mark.asyncio
async def test_meeting_create_post(client, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    scheduled_at = (datetime.now() + timedelta(days=1)).isoformat()
    response = await client.post(
        "/meetings/create",
        data={
            "title": "Test Meeting",
            "scheduled_at": scheduled_at,
            "user_ids": [admin_user.id]
        }
    )
    assert response.status_code == 200
    assert "Test Meeting" in response.text

    app.dependency_overrides.clear()


# ---------------------------
# GET /meetings/edit/{meeting_id} — форма редактирования
# ---------------------------
@pytest.mark.asyncio
async def test_meeting_edit_form(client, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    # Создаем встречу для редактирования
    scheduled_at = (datetime.now() + timedelta(days=1)).isoformat()
    await client.post(
        "/meetings/create",
        data={
            "title": "MeetingEdit",
            "scheduled_at": scheduled_at,
            "user_ids": [admin_user.id]
        }
    )

    response = await client.get("/meetings/edit/1")
    assert response.status_code == 200
    assert "<html" in response.text

    app.dependency_overrides.clear()


# ---------------------------
# POST /meetings/edit/{meeting_id} — редактирование встречи
# ---------------------------
@pytest.mark.asyncio
async def test_meeting_edit_post(client, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    scheduled_at = (datetime.now() + timedelta(days=1)).isoformat()
    await client.post(
        "/meetings/create",
        data={
            "title": "OldMeeting",
            "scheduled_at": scheduled_at,
            "user_ids": [admin_user.id]
        }
    )

    new_scheduled_at = (datetime.now() + timedelta(days=2)).isoformat()
    response = await client.post(
        "/meetings/edit/1",
        data={
            "title": "NewMeeting",
            "scheduled_at": new_scheduled_at,
            "user_ids": [admin_user.id]
        }
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/meetings"

    app.dependency_overrides.clear()


# ---------------------------
# GET /meetings/delete/{meeting_id} — удаление встречи
# ---------------------------
@pytest.mark.asyncio
async def test_meeting_delete(client, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    scheduled_at = (datetime.now() + timedelta(days=1)).isoformat()
    await client.post(
        "/meetings/create",
        data={
            "title": "MeetingToDelete",
            "scheduled_at": scheduled_at,
            "user_ids": [admin_user.id]
        }
    )

    response = await client.get("/meetings/delete/1")
    assert response.status_code == 200

    app.dependency_overrides.clear()

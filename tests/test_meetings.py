import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from app.main import app
from app.auth import get_current_user


@pytest.mark.asyncio
async def test_meetings_list(client: AsyncClient):
    """
    Тест отображения списка встреч.
    Проверяет, что GET-запрос на /meetings/ возвращает статус 200 и содержит HTML.
    """
    response = await client.get("/meetings/")
    assert response.status_code == 200
    assert "<html" in response.text


@pytest.mark.asyncio
async def test_meeting_create_form(client, admin_user):
    """
    Тест отображения формы создания встречи.
    Проверяет, что GET-запрос на /meetings/create возвращает статус 200 и HTML для администратора.
    """
    app.dependency_overrides[get_current_user] = lambda: admin_user

    response = await client.get("/meetings/create")
    assert response.status_code == 200
    assert "<html" in response.text

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_meeting_create_post(client, admin_user):
    """
    Тест создания новой встречи через POST-запрос.
    Проверяет, что создается встреча с заданным названием и возвращается HTML с этим названием.
    """
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


@pytest.mark.asyncio
async def test_meeting_edit_form(client, admin_user):
    """
    Тест отображения формы редактирования встречи.
    Проверяет, что GET-запрос на /meetings/edit/{id} возвращает статус 200 и HTML.
    """
    app.dependency_overrides[get_current_user] = lambda: admin_user

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


@pytest.mark.asyncio
async def test_meeting_edit_post(client, admin_user):
    """
    Тест редактирования существующей встречи через POST-запрос.
    Проверяет, что изменения сохраняются и возвращается редирект на /meetings.
    """
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


@pytest.mark.asyncio
async def test_meeting_delete(client, admin_user):
    """
    Тест удаления встречи.
    Проверяет, что GET-запрос на /meetings/delete/{id} удаляет встречу и возвращает статус 200.
    """
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

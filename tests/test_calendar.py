import pytest
from httpx import AsyncClient
from datetime import datetime, date, timedelta
from app.main import app
from app.auth import get_current_user

@pytest.mark.asyncio
async def test_day_view(client: AsyncClient, admin_user, normal_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    # Создаём задачу на сегодня
    today = datetime.now().date()
    deadline = datetime.now().isoformat()
    await client.post("/tasks/create", data={
        "title": "Task Today",
        "description": "",
        "task_status": "open",
        "deadline": deadline,
        "user_ids": [normal_user.id],
        "first_comment": ""
    })

    # Создаём встречу на сегодня
    await client.post("/meetings/create", data={
        "title": "Meeting Today",
        "scheduled_at": deadline,
        "user_ids": [normal_user.id]
    })

    # Проверяем day_view
    response = await client.get(f"/calendar/day/{today}")
    assert response.status_code == 200
    assert "Task Today" in response.text
    assert "Meeting Today" in response.text

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_month_view(client: AsyncClient, admin_user, normal_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    # Создаём задачу и встречу в этом месяце
    today = datetime.now()
    deadline = today.isoformat()
    await client.post("/tasks/create", data={
        "title": "Task Month",
        "description": "",
        "task_status": "open",
        "deadline": deadline,
        "user_ids": [normal_user.id],
        "first_comment": ""
    })
    await client.post("/meetings/create", data={
        "title": "Meeting Month",
        "scheduled_at": deadline,
        "user_ids": [normal_user.id]
    })

    # Проверяем month_view
    response = await client.get(f"/calendar/month/{today.year}/{today.month}")
    assert response.status_code == 200
    assert "Task Month" in response.text
    assert "Meeting Month" in response.text

    app.dependency_overrides.clear()

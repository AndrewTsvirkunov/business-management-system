import pytest
from httpx import AsyncClient
from datetime import datetime

from app.main import app
from app.auth import get_current_user


@pytest.mark.asyncio
async def test_day_view(client: AsyncClient, admin_user, normal_user):
    """
    Тест для отображения календаря по дню.
    Проверяет, что созданные задачи и встречи на конкретную дату
    корректно отображаются в дневном виде календаря.
    """
    app.dependency_overrides[get_current_user] = lambda: admin_user

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

    await client.post("/meetings/create", data={
        "title": "Meeting Today",
        "scheduled_at": deadline,
        "user_ids": [normal_user.id]
    })

    response = await client.get(f"/calendar/day/{today}")
    assert response.status_code == 200
    assert "Task Today" in response.text
    assert "Meeting Today" in response.text

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_month_view(client: AsyncClient, admin_user, normal_user):
    """
    Тест для отображения календаря по месяцу.
    Проверяет, что созданные задачи и встречи в текущем месяце
    корректно отображаются в месячном виде календаря.
    """
    app.dependency_overrides[get_current_user] = lambda: admin_user

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

    response = await client.get(f"/calendar/month/{today.year}/{today.month}")
    assert response.status_code == 200
    assert "Task Month" in response.text
    assert "Meeting Month" in response.text

    app.dependency_overrides.clear()

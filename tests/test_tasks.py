import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta

from app.main import app
from app.auth import get_current_user


@pytest.mark.asyncio
async def test_tasks_list(client: AsyncClient, admin_user):
    """
    Тест отображения списка задач.
    Проверяет, что GET-запрос на /tasks/ возвращает статус 200 и содержит HTML.
    """
    app.dependency_overrides[get_current_user] = lambda: admin_user

    response = await client.get("/tasks/")
    assert response.status_code == 200
    assert "<html" in response.text

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_task_create_form_admin(client, admin_user):
    """
    Тест отображения формы создания задачи для администратора.
    Проверяет, что GET-запрос на /tasks/create возвращает статус 200 и HTML.
    """
    app.dependency_overrides[get_current_user] = lambda: admin_user

    response = await client.get("/tasks/create")
    assert response.status_code == 200
    assert "<html" in response.text

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_task_create_form_forbidden(client, normal_user):
    """
    Тест запрета создания задачи для обычного пользователя.
    Проверяет, что GET-запрос на /tasks/create возвращает 403 и соответствующее сообщение.
    """
    app.dependency_overrides[get_current_user] = lambda: normal_user

    response = await client.get("/tasks/create")
    assert response.status_code == 403
    assert "User не может создавать задачу" in response.text

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_task_create_post(client, admin_user):
    """
    Тест создания новой задачи через POST-запрос.
    Проверяет, что задача создается с заданными данными и возвращается HTML с названием задачи.
    """
    app.dependency_overrides[get_current_user] = lambda: admin_user

    deadline = (datetime.now() + timedelta(days=1)).isoformat()
    response = await client.post(
        "/tasks/create",
        data={
            "title": "Test Task",
            "description": "Описание задачи",
            "task_status": "open",
            "deadline": deadline,
            "user_ids": [admin_user.id],
            "first_comment": "Первый комментарий"
        }
    )
    assert response.status_code == 200
    assert "Test Task" in response.text

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_task_edit_form(client, admin_user):
    """
    Тест отображения формы редактирования задачи.
    Проверяет, что GET-запрос на /tasks/edit/{id} возвращает HTML для администратора.
    """
    app.dependency_overrides[get_current_user] = lambda: admin_user

    deadline = (datetime.now() + timedelta(days=1)).isoformat()
    await client.post(
        "/tasks/create",
        data={
            "title": "TaskEdit",
            "description": "",
            "task_status": "open",
            "deadline": deadline,
            "user_ids": [admin_user.id],
            "first_comment": "Комментарий"
        }
    )

    response = await client.get("/tasks/edit/1")
    assert response.status_code == 200
    assert "<html" in response.text

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_task_edit_post(client, admin_user):
    """
    Тест редактирования существующей задачи через POST-запрос.
    Проверяет, что изменения сохраняются и возвращается редирект на /tasks.
    """
    app.dependency_overrides[get_current_user] = lambda: admin_user

    deadline = (datetime.now() + timedelta(days=1)).isoformat()
    await client.post(
        "/tasks/create",
        data={
            "title": "OldTask",
            "description": "",
            "task_status": "open",
            "deadline": deadline,
            "user_ids": [admin_user.id],
            "first_comment": "Комментарий"
        }
    )

    new_deadline = (datetime.now() + timedelta(days=2)).isoformat()
    response = await client.post(
        "/tasks/edit/1",
        data={
            "title": "NewTask",
            "description": "Обновлено",
            "task_status": "in_progress",
            "deadline": new_deadline,
            "user_ids": [admin_user.id]
        }
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/tasks"

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_task_delete(client, admin_user):
    """
    Тест удаления задачи.
    Проверяет, что GET-запрос на /tasks/delete/{id} удаляет задачу и возвращает статус 200.
    """
    app.dependency_overrides[get_current_user] = lambda: admin_user

    deadline = (datetime.now() + timedelta(days=1)).isoformat()
    await client.post(
        "/tasks/create",
        data={
            "title": "TaskToDelete",
            "description": "",
            "task_status": "open",
            "deadline": deadline,
            "user_ids": [admin_user.id],
            "first_comment": "Комментарий"
        }
    )

    response = await client.get("/tasks/delete/1")
    assert response.status_code == 200

    app.dependency_overrides.clear()
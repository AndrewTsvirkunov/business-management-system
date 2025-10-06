import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta

from app.main import app
from app.auth import get_current_user

@pytest.mark.asyncio
async def test_tasks_list(client: AsyncClient, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    response = await client.get("/tasks/")
    assert response.status_code == 200
    assert "<html" in response.text

    app.dependency_overrides.clear()


# ---------------------------
# GET /tasks/create — форма создания
# ---------------------------
@pytest.mark.asyncio
async def test_task_create_form_admin(client, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    response = await client.get("/tasks/create")
    assert response.status_code == 200
    assert "<html" in response.text

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_task_create_form_forbidden(client, normal_user):
    app.dependency_overrides[get_current_user] = lambda: normal_user

    response = await client.get("/tasks/create")
    assert response.status_code == 403
    assert "User не может создавать задачу" in response.text

    app.dependency_overrides.clear()


# ---------------------------
# POST /tasks/create — создание задачи
# ---------------------------
@pytest.mark.asyncio
async def test_task_create_post(client, admin_user):
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


# ---------------------------
# GET /tasks/edit/{task_id} — форма редактирования
# ---------------------------
@pytest.mark.asyncio
async def test_task_edit_form(client, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    # Создаём задачу для редактирования
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


# ---------------------------
# POST /tasks/edit/{task_id} — редактирование задачи
# ---------------------------
@pytest.mark.asyncio
async def test_task_edit_post(client, admin_user):
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


# ---------------------------
# GET /tasks/delete/{task_id} — удаление задачи
# ---------------------------
@pytest.mark.asyncio
async def test_task_delete(client, admin_user):
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


# ---------------------------
# POST /tasks/comment/{task_id} — добавление комментария
# ---------------------------
# @pytest.mark.asyncio
# async def test_task_add_comment(client, admin_user):
#     app.dependency_overrides[get_current_user] = lambda: admin_user
#
#     deadline = (datetime.now() + timedelta(days=1)).isoformat()
#     await client.post(
#         "/tasks/create",
#         data={
#             "title": "TaskWithComment",
#             "description": "",
#             "task_status": "open",
#             "deadline": deadline,
#             "user_ids": [admin_user.id],
#             "first_comment": ""
#         }
#     )
#
#     response = await client.post(
#         "/tasks/comment/1",
#         data={"content": "Новый комментарий"}
#     )
#     assert response.status_code == 303
#     assert response.headers["location"] == "/tasks"
#
#     app.dependency_overrides.clear()

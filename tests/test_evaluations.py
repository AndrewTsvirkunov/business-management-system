import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from app.main import app
from app.auth import get_current_user
from app.models import Task


@pytest.mark.asyncio
async def test_evaluations_list(client: AsyncClient, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    response = await client.get("/evaluations/")
    assert response.status_code == 200
    assert "<html" in response.text

    app.dependency_overrides.clear()


# ---------------------------
# GET /evaluations/create — форма создания
# ---------------------------
@pytest.mark.asyncio
async def test_evaluation_create_form_admin(client, admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user

    response = await client.get("/evaluations/create")
    assert response.status_code == 200
    assert "<html" in response.text

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_evaluation_create_form_forbidden(client, normal_user):
    app.dependency_overrides[get_current_user] = lambda: normal_user

    response = await client.get("/evaluations/create")
    assert response.status_code == 403
    assert "User не может ставить оценки" in response.text

    app.dependency_overrides.clear()


# @pytest.mark.asyncio
# async def test_evaluation_create_post(client: AsyncClient, admin_user, normal_user, async_session):
#     app.dependency_overrides[get_current_user] = lambda: admin_user
#
#     # Создаем задачу напрямую в базе
#     task = Task(
#         title="Done Task",
#         description="Task для оценки",
#         status="done",
#         deadline=datetime.now()
#     )
#     task.users.append(normal_user)
#     async_session.add(task)
#     await async_session.commit()
#
#     # Теперь можно создать оценку через эндпоинт
#     response = await client.post(
#         "/evaluations/create",
#         data={
#             "score": 5,
#             "task_title": task.title,
#             "user_name": normal_user.name
#         }
#     )
#     assert response.status_code == 200
#     assert task.title in response.text
#
#     app.dependency_overrides.clear()


# # ---------------------------
# # GET /evaluations/edit/{evaluation_id} — форма редактирования
# # ---------------------------
# @pytest.mark.asyncio
# async def test_evaluation_edit_form(client: AsyncClient, admin_user):
#     app.dependency_overrides[get_current_user] = lambda: admin_user
#
#     # Создаем задачу и оценку для редактирования
#     deadline = (datetime.now() - timedelta(days=1)).isoformat()
#     await client.post(
#         "/tasks/create",
#         data={
#             "title": "TaskToEdit",
#             "description": "",
#             "task_status": "done",
#             "deadline": deadline,
#             "user_ids": [admin_user.id],
#             "first_comment": ""
#         }
#     )
#
#     eval_response = await client.post(
#         "/evaluations/create",
#         data={"score": 5, "task_title": "TaskToEdit", "user_name": admin_user.name}
#     )
#
#     # Предполагаем, что первая оценка имеет id=1
#     response = await client.get("/evaluations/edit/1")
#     assert response.status_code == 200
#     assert "<html" in response.text
#
#     app.dependency_overrides.clear()
#
#
# # ---------------------------
# # POST /evaluations/edit/{evaluation_id} — редактирование оценки
# # ---------------------------
# @pytest.mark.asyncio
# async def test_evaluation_edit_post(client: AsyncClient, admin_user):
#     app.dependency_overrides[get_current_user] = lambda: admin_user
#
#     response = await client.post("/evaluations/edit/1", data={"score": 4})
#     assert response.status_code == 303
#     assert response.headers["location"] == "/evaluations"
#
#     app.dependency_overrides.clear()
#
#
# # ---------------------------
# # GET /evaluations/delete/{evaluation_id} — удаление оценки
# # ---------------------------
# @pytest.mark.asyncio
# async def test_evaluation_delete(client: AsyncClient, admin_user):
#     app.dependency_overrides[get_current_user] = lambda: admin_user
#
#     response = await client.get("/evaluations/delete/1")
#     assert response.status_code == 200
#     assert "Оценка удалена" in response.text
#
#     app.dependency_overrides.clear()
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from fastapi import FastAPI
from sqlalchemy import select
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend

from app.database import engine, async_session
from app.models import User, Team, Task, TaskComment, Meeting, Evaluation
from app.auth import verify_password


class AdminAuth(AuthenticationBackend):
    def __init__(self, secret_key: str):
        super().__init__(secret_key)

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username") or form.get("email")
        password = form.get("password")

        if not username or not password:
            return False

        async with async_session() as session:
            result = await session.execute(select(User).where(User.email == username))
            user = result.scalar_one_or_none()
            if not user:
                return False

            if not verify_password(password, user.hashed_password):
                return False

            if user.role != "admin":
                return False

            request.session.update({"admin_user_id": user.id})
            return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        admin_user_id = request.session.get("admin_user_id")
        if not admin_user_id:
            return False

        async with async_session() as session:
            result = await session.execute(select(User).where(User.id == admin_user_id))
            user = result.scalar_one_or_none()
            return user is not None


class BaseAdmin(ModelView):
    def is_accessible(self, request: Request) -> bool:
        return bool(request.session.get("admin_user_id"))

    def is_visible(self, request: Request) -> bool:
        return bool(request.session.get("admin_user_id"))


class UserAdmin(BaseAdmin, model=User):
    column_list = [User.id, User.name, User.email, User.role]
    column_searchable_list = [User.name, User.email]
    form_columns = [User.name, User.email, User.role, User.hashed_password]


class TeamAdmin(BaseAdmin, model=Team):
    column_list = [Team.id, Team.title]
    form_columns = [Team.title, Team.users]


class TaskAdmin(BaseAdmin, model=Task):
    column_list = [Task.id, Task.title, Task.status, Task.deadline]
    column_searchable_list = [Task.title, Task.description]
    form_columns = [Task.title, Task.description, Task.status, Task.deadline, Task.users]


class TaskCommentAdmin(BaseAdmin, model=TaskComment):
    column_list = [TaskComment.id, TaskComment.content, TaskComment.created_at, TaskComment.task_id, TaskComment.user_id]
    form_columns = [TaskComment.content, TaskComment.task_id, TaskComment.user_id]


class MeetingAdmin(BaseAdmin, model=Meeting):
    column_list = [Meeting.id, Meeting.title, Meeting.scheduled_at]
    form_columns = [Meeting.title, Meeting.scheduled_at, Meeting.users]


class EvaluationAdmin(BaseAdmin, model=Evaluation):
    column_list = [Evaluation.id, Evaluation.score, Evaluation.created_at,
                   Evaluation.task_id, Evaluation.user_id, Evaluation.evaluator_id]
    form_columns = [Evaluation.score, Evaluation.task_id, Evaluation.user_id, Evaluation.evaluator_id]


def init_admin(app: FastAPI, secret_key: str):
    app.add_middleware(SessionMiddleware, secret_key=secret_key)

    auth_backend = AdminAuth(secret_key=secret_key)

    admin = Admin(app=app, engine=engine, authentication_backend=auth_backend, title="BMS Admin")
    admin.add_view(UserAdmin)
    admin.add_view(TeamAdmin)
    admin.add_view(TaskAdmin)
    admin.add_view(TaskCommentAdmin)
    admin.add_view(MeetingAdmin)
    admin.add_view(EvaluationAdmin)

    return admin
from fastapi import FastAPI

from app.routers import users, teams, tasks, task_comments, meetings, evaluations, calendar
from app.admin import init_admin
from app.config import ADMIN_SECRET_KEY


app = FastAPI(title="Business management system")
init_admin(app, secret_key=ADMIN_SECRET_KEY)

app.include_router(users.router)
app.include_router(teams.router)
app.include_router(tasks.router)
app.include_router(task_comments.router)
app.include_router(meetings.router)
app.include_router(evaluations.router)
app.include_router(calendar.router)


@app.get("/", tags=["root"])
async def root():
    return {"message": "Добро пожаловать!"}
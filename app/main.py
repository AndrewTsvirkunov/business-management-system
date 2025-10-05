from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from datetime import date

from app.routers import users, teams, tasks, meetings, evaluations, calendar, login
from app.admin import init_admin
from app.config import ADMIN_SECRET_KEY, templates


app = FastAPI(title="Business management system")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

init_admin(app, secret_key=ADMIN_SECRET_KEY)

app.include_router(login.router)
app.include_router(users.router)
app.include_router(teams.router)
app.include_router(tasks.router)
app.include_router(meetings.router)
app.include_router(evaluations.router)
app.include_router(calendar.router)


@app.get("/")
async def index(request: Request):
    today = date.today()
    return templates.TemplateResponse("index.html", {"request": request, "today": today})
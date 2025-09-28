from fastapi import FastAPI

from app.routers import users, teams, tasks, task_comments, meetings, evaluations


app = FastAPI(title="Business management system")
app.include_router(users.router)
app.include_router(teams.router)
app.include_router(tasks.router)
app.include_router(task_comments.router)
app.include_router(meetings.router)
app.include_router(evaluations.router)


@app.get("/", tags=["root"])
async def root():
    return {"message": "Добро пожаловать!"}
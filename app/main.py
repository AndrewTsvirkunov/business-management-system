from fastapi import FastAPI

from app.routers import users


app = FastAPI(title="Business management system")
app.include_router(users.router)


@app.get("/", tags=["root"])
async def root():
    return {"message": "Добро пожаловать!"}
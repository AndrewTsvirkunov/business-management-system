from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from datetime import datetime

from app.models import Task, User
from app.shemas import TaskCreate, TaskRead, TaskUpdate
from app.database import get_async_db


router = APIRouter(prefix="/tasks", tags=["tasks"])

templates = Jinja2Templates(directory="app/templates")


# @router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
# async def create_task(task: TaskCreate, db:AsyncSession = Depends(get_async_db)):
#     users = []
#     if task.user_ids:
#         result = await db.execute(select(User).where(User.id.in_(task.user_ids)))
#         users = result.scalars().all()
#
#     db_task = Task(
#         title=task.title,
#         description=task.description,
#         status=task.status,
#         deadline=task.deadline,
#         users=users
#     )
#     db.add(db_task)
#     await db.commit()
#     return db_task
#
#
# @router.get("/{task_id}", response_model=TaskRead)
# async def get_task_info(task_id: int, db: AsyncSession = Depends(get_async_db)):
#     task = await db.get(Task, task_id)
#     if not task:
#         raise HTTPException(status_code=404, detail="Task not found")
#     return task
#
#
# @router.delete("/{task_id}", response_model=TaskRead)
# async def delete_task(task_id: int, db: AsyncSession = Depends(get_async_db)):
#     task = await db.get(Task, task_id)
#     if not task:
#         raise HTTPException(status_code=404, detail="Task not found")
#     await db.delete(task)
#     await db.commit()
#     return {"message": f"Task {task_id} deleted"}
#
#
# @router.patch("/{task_id}", response_model=TaskRead)
# async def update_task(task_id: int, task: TaskUpdate, db: AsyncSession = Depends(get_async_db)):
#     db_task = await db.get(Task, task_id)
#     if not db_task:
#         raise HTTPException(status_code=404, detail="Task not found")
#
#     update_data = task.model_dump(exclude_unset=True)
#
#     if "user_ids" in update_data:
#         user_ids = update_data.pop("user_ids")
#         if user_ids is not None:
#             result = await db.execute(select(User).where(User.id.in_(user_ids)))
#             users = result.scalars().all()
#             db_task.users = users
#
#     for field, value in update_data.items():
#         setattr(db_task, field, value)
#
#     await db.commit()
#     return db_task


# ---------------------------------------------------------------------

@router.get("/")
async def tasks_list(request: Request, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        select(Task).options(selectinload(Task.users))
    )
    tasks = result.scalars().all()
    return templates.TemplateResponse(
        "tasks/tasks_list.html",
        {"request": request, "tasks": tasks}
    )


@router.get("/create")
async def task_create_form(request: Request, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return templates.TemplateResponse("tasks/task_create.html", {"request": request, "users": users})


@router.post("/create")
async def task_create(
        request: Request,
        title: str = Form(...),
        description: str = Form(""),
        task_status: str = Form("open"),
        deadline: str = Form(...),
        user_ids: list[int] = Form([]),
        db: AsyncSession = Depends(get_async_db)
):
    deadline_dt = datetime.fromisoformat(deadline)

    result = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = result.scalars().all()

    task = Task(title=title, description=description, status=task_status, deadline=deadline_dt, users=users)
    db.add(task)
    await db.commit()
    return templates.TemplateResponse(
        "tasks/task_created.html",
        {"request": request, "task": task, "users": users}
    )


@router.get("/edit/{task_id}")
async def task_edit_form(request: Request, task_id: int, db: AsyncSession = Depends(get_async_db)):
    task = await db.get(Task, task_id)

    result = await db.execute(select(User))
    users = result.scalars().all()

    return templates.TemplateResponse(
        "tasks/task_edit.html",
        {"request": request, "task": task, "users": users}
    )


@router.post("/edit/{task_id}")
async def task_edit(
        request: Request,
        task_id: int,
        title: str = Form(...),
        description: str = Form(""),
        task_status: str = Form(...),
        deadline: str = Form(...),
        user_ids: list[int] = Form([]),
        db: AsyncSession = Depends(get_async_db)
):
    task = await db.get(Task, task_id)

    task.title = title
    task.description = description
    task.status = task_status
    task.deadline = datetime.fromisoformat(deadline)

    result = await db.execute(select(User).where(User.id.in_(user_ids)))
    task.users = result.scalars().all()

    await db.commit()
    return RedirectResponse(url="/tasks", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/delete/{task_id}")
async def task_delete(task_id: int, db: AsyncSession = Depends(get_async_db)):
    task = await db.get(Task, task_id)
    await db.delete(task)
    await db.commit()
    return HTMLResponse(f"Задача {task.title} удалена")
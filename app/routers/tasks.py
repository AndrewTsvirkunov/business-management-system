from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from datetime import datetime

from app.models import Task, User, TaskComment
from app.shemas import TaskCreate, TaskRead, TaskUpdate
from app.database import get_async_db
from app.auth import get_current_manager, get_current_user_or_manager, get_current_user, get_curr_user


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
async def tasks_list(request: Request, db: AsyncSession = Depends(get_async_db),
                     current_user: User = Depends(get_curr_user)):
    result = await db.execute(
        select(Task).options(
            selectinload(Task.users),
            selectinload(Task.comments)
        )
    )
    tasks = result.scalars().all()
    return templates.TemplateResponse(
        "tasks/tasks_list.html",
        {"request": request, "tasks": tasks, "current_user": current_user}
    )


@router.get("/create")
async def task_create_form(request: Request, db: AsyncSession = Depends(get_async_db),
                           current_user: User = Depends(get_curr_user)):
    result_users = await db.execute(select(User))
    users = result_users.scalars().all()

    return templates.TemplateResponse(
        "tasks/task_create.html",
        {"request": request, "users": users, "current_user": current_user}
    )


@router.post("/create")
async def task_create(
        request: Request,
        title: str = Form(...),
        description: str = Form(""),
        task_status: str = Form("open"),
        deadline: str = Form(...),
        user_ids: list[int] = Form([]),
        first_comment: str = Form(...),
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_curr_user)
):
    deadline_dt = datetime.fromisoformat(deadline)

    result = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = result.scalars().all()

    task = Task(title=title, description=description, status=task_status, deadline=deadline_dt, users=users)

    db.add(task)
    await db.flush()

    if first_comment:
        comment = TaskComment(content=first_comment, task_id=task.id, user_id=current_user.id)
        db.add(comment)

    await db.commit()
    return templates.TemplateResponse(
        "tasks/task_created.html",
        {"request": request, "task": task, "users": users, "current_user": current_user}
    )


@router.get("/edit/{task_id}")
async def task_edit_form(request: Request, task_id: int, db: AsyncSession = Depends(get_async_db),
                         current_user: User = Depends(get_curr_user)):
    result_task = await db.execute(
        select(Task).options(selectinload(Task.users)).where(Task.id == task_id)
    )
    task = result_task.scalars().first()

    if task.id != current_user.id and current_user.role != "manager":
        raise HTTPException(status_code=403, detail="Нет доступа")

    result_users = await db.execute(select(User))
    users = result_users.scalars().all()

    return templates.TemplateResponse(
        "tasks/task_edit.html",
        {"request": request, "task": task, "users": users, "current_user": current_user}
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
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_curr_user)
):
    task = await db.get(Task, task_id)

    if task.id != current_user.id and current_user.role != "manager":
        raise HTTPException(status_code=403, detail="Нет доступа")

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


@router.get("/comment/{task_id}")
async def add_comment_form(request: Request, task_id: int):
    return templates.TemplateResponse(
        "tasks/add_comment.html",
        {"request": request}
    )


@router.post("/comment/{task_id}")
async def add_comment(
        task_id: int,
        content: str = Form(...),
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_curr_user)
):
    comment = TaskComment(content=content, task_id=task_id, user_id=current_user.id)
    db.add(comment)
    await db.commit()
    return RedirectResponse(url="/tasks", status_code=303)
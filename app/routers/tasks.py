from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from datetime import datetime

from app.models import Task, User, TaskComment, Team
from app.database import get_async_db
from app.auth import get_current_user
from app.config import templates


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/")
async def tasks_list(request: Request, db: AsyncSession = Depends(get_async_db),
                     current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        result = await db.execute(
            select(Task)
            .options(selectinload(Task.users), selectinload(Task.comments))
        )
        tasks = result.scalars().all()

    elif current_user.role == "manager":
        result_teams = await db.execute(
            select(Team.id).where(Team.manager_id == current_user.id)
        )
        team_ids = result_teams.scalars().all()

        if team_ids:
            result = await db.execute(
                select(Task)
                .options(selectinload(Task.users), selectinload(Task.comments))
                .where(Task.users.any(User.teams.any(Team.id.in_(team_ids))))
            )
            tasks = result.scalars().all()
        else:
            tasks = []

    else:
        result = await db.execute(
            select(Task)
            .options(selectinload(Task.users), selectinload(Task.comments))
            .where(Task.users.any(User.id == current_user.id))
        )
        tasks = result.scalars().all()

    return templates.TemplateResponse(
        request,
        "tasks/tasks_list.html",
        {"request": request, "tasks": tasks, "current_user": current_user}
    )


@router.get("/create")
async def task_create_form(request: Request, db: AsyncSession = Depends(get_async_db),
                           current_user: User = Depends(get_current_user)):
    if current_user.role == "user":
        raise HTTPException(status_code=403, detail="User не может создавать задачу")

    if current_user.role == "admin":
        result_users = await db.execute(select(User))
        users = result_users.scalars().all()

    elif current_user.role == "manager":
        result_users = await db.execute(
            select(User).where(User.teams.any(Team.manager_id == current_user.id)))
        users = result_users.scalars().all()

    return templates.TemplateResponse(
        request,
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
        current_user: User = Depends(get_current_user)
):
    if current_user.role == "user":
        raise HTTPException(status_code=403, detail="User не может создавать задачу")

    deadline_dt = datetime.fromisoformat(deadline)

    if current_user.role == "admin":
        result = await db.execute(select(User).where(User.id.in_(user_ids)))
        users = result.scalars().all()

    elif current_user.role == "manager":
        result = await db.execute(
            select(User)
            .where(User.id.in_(user_ids))
            .where(User.teams.any(Team.manager_id == current_user.id))
        )
        users = result.scalars().all()

    task = Task(title=title, description=description, status=task_status, deadline=deadline_dt, users=users)

    db.add(task)
    await db.flush()

    if first_comment:
        comment = TaskComment(content=first_comment, task_id=task.id, user_id=current_user.id)
        db.add(comment)

    await db.commit()
    return templates.TemplateResponse(
        request,
        "tasks/task_created.html",
        {"request": request, "task": task, "users": users, "current_user": current_user}
    )


@router.get("/edit/{task_id}")
async def task_edit_form(request: Request, task_id: int, db: AsyncSession = Depends(get_async_db),
                         current_user: User = Depends(get_current_user)):
    result_task = await db.execute(
        select(Task).options(selectinload(Task.users)).where(Task.id == task_id)
    )
    task = result_task.scalars().first()

    if current_user.role != "admin" and current_user not in task.users and current_user.role != "manager":
        raise HTTPException(status_code=403, detail="У вас нет доступа к этой задаче")

    result_users = await db.execute(select(User))
    users = result_users.scalars().all()

    return templates.TemplateResponse(
        request,
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
        current_user: User = Depends(get_current_user)
):
    result_task = await db.execute(
        select(Task).options(selectinload(Task.users)).where(Task.id == task_id))
    task = result_task.scalars().first()

    if current_user.role != "admin" and current_user not in task.users and current_user.role != "manager":
        raise HTTPException(status_code=403, detail="У вас нет доступа к этой задаче")

    task.title = title
    task.description = description
    task.status = task_status
    task.deadline = datetime.fromisoformat(deadline)

    result = await db.execute(select(User).where(User.id.in_(user_ids)))
    task.users = result.scalars().all()

    await db.commit()
    return RedirectResponse(url="/tasks", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/delete/{task_id}")
async def task_delete(task_id: int, db: AsyncSession = Depends(get_async_db),
                      current_user: User = Depends(get_current_user)):
    task = await db.get(Task, task_id)

    if current_user.role != "admin" and current_user not in task.users and current_user.role != "manager":
        raise HTTPException(status_code=403, detail="У вас нет доступа к этой задаче")

    await db.delete(task)
    await db.commit()
    return HTMLResponse(f"Задача {task.title} удалена")


@router.get("/comment/{task_id}")
async def add_comment_form(request: Request, task_id: int):
    return templates.TemplateResponse(
        request,
        "tasks/add_comment.html",
        {"request": request}
    )


@router.post("/comment/{task_id}")
async def add_comment(
        task_id: int,
        content: str = Form(...),
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_user)
):
    comment = TaskComment(content=content, task_id=task_id, user_id=current_user.id)
    db.add(comment)
    await db.commit()
    return RedirectResponse(url="/tasks", status_code=303)
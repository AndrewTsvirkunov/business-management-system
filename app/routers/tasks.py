from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update

from app.models import Task, User
from app.shemas import TaskCreate, TaskRead, TaskUpdate
from app.database import get_async_db


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, db:AsyncSession = Depends(get_async_db)):
    users = []
    if task.user_ids:
        result = await db.execute(select(User).where(User.id.in_(task.user_ids)))
        users = result.scalars().all()

    db_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        deadline=task.deadline,
        users=users
    )
    db.add(db_task)
    await db.commit()
    return db_task


@router.get("/{task_id}", response_model=TaskRead)
async def get_task_info(task_id: int, db: AsyncSession = Depends(get_async_db)):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", response_model=TaskRead)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_async_db)):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.commit()
    return {"message": f"Task {task_id} deleted"}


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(task_id: int, task: TaskUpdate, db: AsyncSession = Depends(get_async_db)):
    db_task = await db.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task.model_dump(exclude_unset=True)

    if "user_ids" in update_data:
        user_ids = update_data.pop("user_ids")
        if user_ids is not None:
            result = await db.execute(select(User).where(User.id.in_(user_ids)))
            users = result.scalars().all()
            db_task.users = users

    for field, value in update_data.items():
        setattr(db_task, field, value)

    await db.commit()
    return db_task

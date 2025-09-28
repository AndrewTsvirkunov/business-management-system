from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import TaskComment, User, Task
from app.shemas import TaskCommentCreate, TaskCommentRead
from app.database import get_async_db


router = APIRouter(prefix="/task-comments", tags=["task-comments"])


@router.post("/", response_model=TaskCommentRead, status_code=status.HTTP_201_CREATED)
async def create_task_comment(comment: TaskCommentCreate, db: AsyncSession = Depends(get_async_db)):
    task = await db.get(Task, comment.task_id)
    user = await db.get(User, comment.user_id)

    if not task or not user:
        raise HTTPException(status_code=404, detail="Task or user not found")

    db_comment = TaskComment(
        content=comment.content,
        created_at=comment.created_at,
        task_id=comment.task_id,
        user_id=comment.user_id
    )
    db.add(db_comment)
    await db.commit()
    return db_comment


@router.get("/{task_id}", response_model=list[TaskCommentRead])
async def get_task_comments(task_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(TaskComment).where(TaskComment.task_id == task_id))
    comments = result.scalars().all()
    if not comments:
        raise HTTPException(status_code=404, detail="Task not found")
    return comments
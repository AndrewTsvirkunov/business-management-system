from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Evaluation, User, Task
from app.shemas import EvaluationCreate, EvaluationRead
from app.database import get_async_db


router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.post("/", response_model=EvaluationRead, status_code=status.HTTP_201_CREATED)
async def create_evaluation(evaluation: EvaluationCreate, db: AsyncSession = Depends(get_async_db)):
    task = await db.get(Task, evaluation.task_id)
    user = await db.get(User, evaluation.user_id)
    evaluator = await db.get(User, evaluation.evaluator_id)

    if not task or not user or not evaluator:
        raise HTTPException(status_code=404, detail="Task or user or evaluator not found")

    db_evaluation = Evaluation(
        score=evaluation.score,
        created_at=evaluation.created_at,
        task_id=evaluation.task_id,
        user_id=evaluation.user_id,
        evaluator_id=evaluation.evaluator_id
    )
    db.add(db_evaluation)
    await db.commit()
    return db_evaluation


@router.get("/{user_id}", response_model=list[EvaluationRead])
async def get_evaluation(user_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Evaluation).where(Evaluation.user_id == user_id))
    evaluation = result.scalars().all()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return evaluation


@router.delete("/{user_id}")
async def delete_evaluation(evaluation_id: int, db: AsyncSession = Depends(get_async_db)):
    evaluation = await db.get(Evaluation, evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    await db.delete(evaluation)
    await db.commit()
    return {"message": f"Evaluate {evaluation_id} for user {evaluation.user_id} deleted"}
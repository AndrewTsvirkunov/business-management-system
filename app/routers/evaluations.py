from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from datetime import datetime

from app.models import Evaluation, User, Task
from app.database import get_async_db
from app.config import templates


router = APIRouter(prefix="/evaluations", tags=["evaluations"])

# templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def evaluations_list(request: Request, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        select(Evaluation).options(
            selectinload(Evaluation.task),
            selectinload(Evaluation.user),
            selectinload(Evaluation.evaluator)
        )
    )
    evaluations = result.scalars().all()

    return templates.TemplateResponse(
        "evaluations/evaluations_list.html",
        {"request": request, "evaluations": evaluations}
    )


@router.get("/create")
async def evaluation_create_form(request: Request, db: AsyncSession = Depends(get_async_db)):
    result_tasks = await db.execute(select(Task))
    tasks = result_tasks.scalars().all()

    result_users = await db.execute(select(User))
    users = result_users.scalars().all()

    return templates.TemplateResponse(
        "evaluations/evaluation_create.html",
        {"request": request, "tasks": tasks, "users": users}
    )


@router.post("/create")
async def evaluation_created(
        request: Request,
        score: int = Form(..., ge=1, le=5),
        task_title: str = Form(...),
        user_name: str = Form(...),
        evaluator_name: str = Form(...),
        db: AsyncSession = Depends(get_async_db)
):
    result_task = await db.execute(select(Task).where(Task.title == task_title))
    task = result_task.scalars().first()

    result_user = await db.execute(select(User).where(User.name == user_name))
    user = result_user.scalars().first()

    result_evaluator = await db.execute(select(User).where(User.name == evaluator_name))
    evaluator = result_evaluator.scalars().first()

    if user not in task.users:
        return HTMLResponse(
            content=f"<h3 style='color:red;'>Ошибка:</h3><p>Пользователь: {user.name} не назначен на задачу {task.title}</p>",
            status_code=400
        )

    evaluation = Evaluation(
        score=score,
        # created_at=datetime.now(),
        task_id=task.id,
        user_id=user.id,
        evaluator_id=evaluator.id
    )
    db.add(evaluation)
    await db.commit()

    return templates.TemplateResponse(
        "evaluations/evaluation_created.html",
        {"request": request, "evaluation": evaluation}
    )


@router.get("/edit/{evaluation_id}")
async def evaluation_edit_form(request: Request, evaluation_id: int, db: AsyncSession = Depends(get_async_db)):
    evaluation = await db.get(Evaluation, evaluation_id)

    result_users = await db.execute(select(User))
    users = result_users.scalars().all()

    return templates.TemplateResponse(
        "evaluations/evaluation_edit.html",
        {"request": request, "evaluation": evaluation, "users": users}
    )


@router.post("/edit/{evaluation_id}")
async def evaluation_edit(
        request: Request,
        evaluation_id: int,
        score: int = Form(..., ge=1, le=5),
        user_name: str = Form(...),
        evaluator_name: str = Form(...),
        db: AsyncSession = Depends(get_async_db)
):
    evaluation = await db.get(Evaluation, evaluation_id)

    result_user = await db.execute(select(User).where(User.name == user_name))
    user = result_user.scalars().first()

    result_evaluator = await db.execute(select(User).where(User.name == evaluator_name))
    evaluator = result_evaluator.scalars().first()

    evaluation.score = score
    # evaluation.created_at = datetime.now()
    evaluation.user_id = user.id
    evaluation.evaluator_id = evaluator.id

    await db.commit()
    return RedirectResponse(url="/evaluations", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/delete/{evaluation_id}")
async def evaluation_delete(evaluation_id: int, db: AsyncSession = Depends(get_async_db)):
    evaluation = await db.get(Evaluation, evaluation_id)
    await db.delete(evaluation)
    await db.commit()
    return HTMLResponse(f"Оценка удалена")
from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from datetime import datetime

from app.models import Evaluation, User, Task, Team
from app.database import get_async_db
from app.config import templates
from app.auth import get_current_user


router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.get("/")
async def evaluations_list(request: Request, db: AsyncSession = Depends(get_async_db),
                           current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        result = await db.execute(
            select(Evaluation).options(
                selectinload(Evaluation.task),
                selectinload(Evaluation.user),
                selectinload(Evaluation.evaluator)
            )
        )
        evaluations = result.scalars().all()

    elif current_user.role == "manager":
        result_teams = await db.execute(
            select(Team.id).where(Team.manager_id == current_user.id)
        )
        team_ids = result_teams.scalars().all()

        if team_ids:
            result = await db.execute(
                select(Evaluation)
                .options(
                    selectinload(Evaluation.task),
                    selectinload(Evaluation.user),
                    selectinload(Evaluation.evaluator),
                )
                .where(Evaluation.user.has(User.teams.any(Team.id.in_(team_ids))))
            )
            evaluations = result.scalars().all()
        else:
            evaluations = []

    else:
        result = await db.execute(
            select(Evaluation)
            .options(
                selectinload(Evaluation.task),
                selectinload(Evaluation.user),
                selectinload(Evaluation.evaluator)
            )
            .where(Evaluation.user_id == current_user.id)
        )
        evaluations = result.scalars().all()

    return templates.TemplateResponse(
        "evaluations/evaluations_list.html",
        {"request": request, "evaluations": evaluations, "current_user": current_user}
    )


@router.get("/create")
async def evaluation_create_form(request: Request, db: AsyncSession = Depends(get_async_db),
                                 current_user: User = Depends(get_current_user)):
    result_tasks = await db.execute(select(Task))
    tasks = result_tasks.scalars().all()

    if current_user.role == "admin":
        result_users = await db.execute(select(User))
    elif current_user.role == "manager":
        result_teams = await db.execute(select(Team.id).where(Team.manager_id == current_user.id))
        team_ids = result_teams.scalars().all()
        result_users = await db.execute(
            select(User).where(User.teams.any(Team.id.in_(team_ids)))
        )
    else:
        return HTMLResponse("User не может ставить оценки", status_code=403)

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
        # evaluator_name: str = Form(...),
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_user)
):
    result_task = await db.execute(select(Task).where(Task.title == task_title))
    task = result_task.scalars().first()

    if task.status != "done":
        return HTMLResponse(
            f"Нельзя оценивать незавершённую задачу: {task.title}",
            status_code=400
        )

    result_user = await db.execute(select(User).where(User.name == user_name))
    user = result_user.scalars().first()

    # result_evaluator = await db.execute(select(User).where(User.name == evaluator_name))
    # evaluator = result_evaluator.scalars().first()

    if current_user.role == "user":
        return HTMLResponse("User не может ставить оценки", status_code=403)

    if current_user.role == "manager":
        result_teams = await db.execute(select(Team.id).where(Team.manager_id == current_user.id))
        team_ids = result_teams.scalars().all()
        if not any(team.id in team_ids for team in user.teams):
            return HTMLResponse("Этого пользователя нет ни в одной из ваших команд", status_code=403)

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
        evaluator_id=current_user.id
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
        # user_name: str = Form(...),
        # evaluator_name: str = Form(...),
        db: AsyncSession = Depends(get_async_db)
):
    evaluation = await db.get(Evaluation, evaluation_id)

    # result_user = await db.execute(select(User).where(User.name == user_name))
    # user = result_user.scalars().first()
    #
    # result_evaluator = await db.execute(select(User).where(User.name == evaluator_name))
    # evaluator = result_evaluator.scalars().first()

    evaluation.score = score
    # evaluation.created_at = datetime.now()
    # evaluation.user_id = user.id
    # evaluation.evaluator_id = evaluator.id

    await db.commit()
    return RedirectResponse(url="/evaluations", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/delete/{evaluation_id}")
async def evaluation_delete(evaluation_id: int, db: AsyncSession = Depends(get_async_db)):
    evaluation = await db.get(Evaluation, evaluation_id)
    await db.delete(evaluation)
    await db.commit()
    return HTMLResponse(f"Оценка удалена")
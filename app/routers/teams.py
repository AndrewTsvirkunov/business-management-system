from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.database import get_async_db
from app.models import Team, User
from app.config import templates


router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("/")
async def teams_list(request: Request, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        select(Team).options(selectinload(Team.users))
    )
    teams = result.scalars().all()
    return templates.TemplateResponse(
        "teams/teams_list.html",
        {"request": request, "teams": teams}
    )


@router.get("/create")
async def team_create_form(request: Request, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return templates.TemplateResponse(
        "teams/team_create.html",
        {"request": request, "users": users}
    )


@router.post("/create")
async def team_create(
        request: Request,
        title: str = Form(...),
        user_ids: list[int] = Form([]),
        db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = result.scalars().all()

    team = Team(title=title, users=users)
    db.add(team)
    await db.commit()
    return RedirectResponse(url="/teams", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/edit/{team_id}")
async def team_edit_form(request: Request, team_id: int, db: AsyncSession = Depends(get_async_db)):
    team = await db.get(Team, team_id)

    result = await db.execute(select(User))
    users = result.scalars().all()

    return templates.TemplateResponse(
        "teams/team_edit.html",
        {"request": request, "team": team, "users": users}
    )


@router.post("/edit/{team_id}")
async def team_edit(
        request: Request,
        team_id: int,
        title: str = Form(...),
        user_ids: list[int] = Form([]),
        db: AsyncSession = Depends(get_async_db)
):
    team = await db.get(Team, team_id)

    result = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = result.scalars().all()

    team.title = title
    team.users = users

    await db.commit()
    return RedirectResponse(url="/teams", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/delete/{team_id}")
async def team_delete(team_id: int, db: AsyncSession = Depends(get_async_db)):
    team = await db.get(Team, team_id)
    await db.delete(team)
    await db.commit()
    return RedirectResponse(url="/teams", status_code=status.HTTP_303_SEE_OTHER)
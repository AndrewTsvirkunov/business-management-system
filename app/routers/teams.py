from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.database import get_async_db
from app.models import Team, User
from app.config import templates
from app.auth import get_current_user


router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("/")
async def teams_list(request: Request, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        select(Team).options(selectinload(Team.users))
    )
    teams = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "teams/teams_list.html",
        {"request": request, "teams": teams}
    )


@router.get("/create")
async def team_create_form(request: Request, db: AsyncSession = Depends(get_async_db),
                           current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        return HTMLResponse("Только admin может создавать команды", status_code=403)
    result = await db.execute(select(User))
    users = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "teams/team_create.html",
        {"request": request, "users": users}
    )


@router.post("/create")
async def team_create(
        request: Request,
        title: str = Form(...),
        user_ids: list[int] = Form([]),
        manager_id: int|None = None,
        db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = result.scalars().all()

    team = Team(title=title, users=users)

    if manager_id:
        manager = await db.get(User, manager_id)
        if manager and manager.role == "manager":
            team.manager = manager

    db.add(team)
    await db.commit()
    return templates.TemplateResponse(
        request,
        "teams/team_created.html",
        {"request": request, "team": team}
    )


@router.get("/edit/{team_id}")
async def team_edit_form(request: Request, team_id: int, db: AsyncSession = Depends(get_async_db)):
    team = await db.get(Team, team_id)

    result = await db.execute(select(User))
    users = result.scalars().all()

    return templates.TemplateResponse(
        request,
        "teams/team_edit.html",
        {"request": request, "team": team, "users": users}
    )


@router.post("/edit/{team_id}")
async def team_edit(
        request: Request,
        team_id: int,
        title: str = Form(...),
        user_ids: list[int] = Form([]),
        manager_id: int|None = None,
        db: AsyncSession = Depends(get_async_db)
):
    team = await db.get(Team, team_id)

    result = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = result.scalars().all()

    team.title = title
    team.users = users

    if manager_id:
        manager = await db.get(User, manager_id)
        if manager and manager.role == "manager":
            team.manager = manager
    else:
        team.manager = None

    await db.commit()
    return RedirectResponse(url="/teams", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/delete/{team_id}")
async def team_delete(team_id: int, db: AsyncSession = Depends(get_async_db)):
    team = await db.get(Team, team_id)
    await db.delete(team)
    await db.commit()
    return RedirectResponse(url="/teams", status_code=status.HTTP_303_SEE_OTHER)
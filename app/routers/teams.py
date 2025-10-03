from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.database import get_async_db
from app.shemas import TeamCreate, TeamRead, TeamUpdate
from app.models import Team, User


router = APIRouter(prefix="/teams", tags=["teams"])

template = Jinja2Templates(directory="app/templates")


# @router.post("/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
# async def create_team(team: TeamCreate, db: AsyncSession = Depends(get_async_db)):
#     users = []
#     if team.user_ids:
#         result = await db.execute(select(User).where(User.id.in_(team.user_ids)))
#         users = result.scalars().all()
#     db_team = Team(
#         title=team.title,
#         users=users
#     )
#     db.add(db_team)
#     await db.commit()
#     return db_team
#
#
# @router.get("/{team_id}", response_model=TeamRead)
# async def get_team(team_id: int, db: AsyncSession = Depends(get_async_db)):
#     team = await db.get(Team, team_id)
#     if not team:
#         raise HTTPException(status_code=404, detail="Team not found")
#     return team
#
#
# @router.delete("/{team_id}")
# async def delete_team(team_id: int, db: AsyncSession = Depends(get_async_db)):
#     team = await db.get(Team, team_id)
#     if not team:
#         raise HTTPException(status_code=404, detail="Team not found")
#     await db.delete(team)
#     await db.commit()
#     return {"message": f"Team {team.title} deleted"}
#
#
# @router.patch("/{team_id}", response_model=TeamRead)
# async def update_team(team_id: int, team: TeamUpdate, db: AsyncSession = Depends(get_async_db)):
#     db_team = await db.get(Team, team_id)
#     if not db_team:
#         raise HTTPException(status_code=404, detail="Team not found")
#
#     update_data = team.model_dump(exclude_unset=True)
#
#     if "user_ids" in update_data:
#         user_ids = update_data.pop("user_ids")
#         if user_ids is not None:
#             result = await db.execute(select(User).where(User.id.in_(user_ids)))
#             users = result.scalars().all()
#             db_team.users = users
#
#     for field, value in update_data.items():
#         setattr(db_team, field, value)
#
#     await db.commit()
#     return db_team

# --------------------------------------------------------------------------------------------

@router.get("/")
async def teams_list(request: Request, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        select(Team).options(selectinload(Team.users))
    )
    teams = result.scalars().all()
    return template.TemplateResponse(
        "teams/teams_list.html",
        {"request": request, "teams": teams}
    )


@router.get("/create")
async def team_create_form(request: Request, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return template.TemplateResponse(
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

    return template.TemplateResponse(
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
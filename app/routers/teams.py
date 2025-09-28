from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_async_db
from app.shemas import TeamCreate, TeamRead, TeamUpdate
from app.models import Team, User


router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
async def create_team(team: TeamCreate, db: AsyncSession = Depends(get_async_db)):
    users = []
    if team.user_ids:
        result = await db.execute(select(User).where(User.id.in_(team.user_ids)))
        users = result.scalars().all()
    db_team = Team(
        title=team.title,
        users=users
    )
    db.add(db_team)
    await db.commit()
    return db_team


@router.get("/{team_id}", response_model=TeamRead)
async def get_team(team_id: int, db: AsyncSession = Depends(get_async_db)):
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.delete("/{team_id}")
async def delete_team(team_id: int, db: AsyncSession = Depends(get_async_db)):
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    await db.delete(team)
    await db.commit()
    return {"message": f"Team {team.title} deleted"}


@router.patch("/{team_id}", response_model=TeamRead)
async def update_team(team_id: int, team: TeamUpdate, db: AsyncSession = Depends(get_async_db)):
    db_team = await db.get(Team, team_id)
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")

    update_data = team.model_dump(exclude_unset=True)

    if "user_ids" in update_data:
        user_ids = update_data.pop("user_ids")
        if user_ids is not None:
            result = await db.execute(select(User).where(User.id.in_(user_ids)))
            users = result.scalars().all()
            db_team.users = users

    for field, value in update_data.items():
        setattr(db_team, field, value)

    await db.commit()
    return db_team

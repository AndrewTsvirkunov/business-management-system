from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.shemas import TeamCreate, TeamRead
from app.models import Team, User


router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
async def create_team(team: TeamCreate, db: AsyncSession = Depends(get_async_db)):
    db_team = Team(title=team.title)
    db.add(db_team)
    await db.commit()
    return db_team


@router.post("/{team_id}/add-user/{user_id}")
async def add_user_to_team(team_id: int, user_id: int, db: AsyncSession = Depends(get_async_db)):
    team = await db.get(Team, team_id)
    user = await db.get(User, user_id)

    if not team or not user:
        raise HTTPException(status_code=404, detail="User or team not found")

    if user not in team.users:
        team.users.append(user)

    await db.commit()
    return {"message": f"User {user_id} added to team {team_id}"}


@router.get("/{team_id}/users")
async def get_team_users(team_id: int, db: AsyncSession = Depends(get_async_db)):
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team.users

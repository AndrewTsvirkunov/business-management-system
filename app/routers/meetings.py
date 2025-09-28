from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Meeting, User
from app.shemas import MeetingCreate, MeetingRead, MeetingUpdate
from app.database import get_async_db


router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.post("/", response_model=MeetingRead, status_code=status.HTTP_201_CREATED)
async def create_meeting(meeting: MeetingCreate, db: AsyncSession = Depends(get_async_db)):
    users = []
    if meeting.user_ids:
        result = await db.execute(select(User).where(User.id.in_(meeting.user_ids)))
        users = result.scalars().all()

    db_meeting = Meeting(
        title=meeting.title,
        scheduled_at=meeting.scheduled_at,
        users=users
    )
    db.add(db_meeting)
    await db.commit()
    return db_meeting


@router.get("/{meeting_id}", response_model=MeetingRead)
async def get_meeting(meeting_id: int, db: AsyncSession = Depends(get_async_db)):
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.delete("/{meeting_id}")
async def delete_meeting(meeting_id: int, db: AsyncSession = Depends(get_async_db)):
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    await db.delete(meeting)
    await db.commit()
    return {"message": f"Meeting {meeting_id} deleted"}


@router.patch("/{meeting_id}", response_model=MeetingRead)
async def update_meeting(meeting_id: int, meeting: MeetingUpdate, db: AsyncSession = Depends(get_async_db)):
    db_meeting = await db.get(Meeting, meeting_id)
    if not db_meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    update_data = meeting.model_dump(exclude_unset=True)

    if "user_ids" in update_data:
        user_ids = update_data.pop("user_ids")
        if user_ids is not None:
            result = await db.execute(select(User).where(User.id.in_(user_ids)))
            users = result.scalars().all()
            db_meeting.users = users

    for field, value in update_data.items():
        setattr(db_meeting, field, value)

    await db.commit()
    return db_meeting

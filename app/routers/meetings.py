from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from datetime import datetime

from app.models import Meeting, User
from app.shemas import MeetingCreate, MeetingRead, MeetingUpdate
from app.database import get_async_db


router = APIRouter(prefix="/meetings", tags=["meetings"])

templates = Jinja2Templates(directory="app/templates")


# @router.post("/", response_model=MeetingRead, status_code=status.HTTP_201_CREATED)
# async def create_meeting(meeting: MeetingCreate, db: AsyncSession = Depends(get_async_db)):
#     users = []
#     if meeting.user_ids:
#         result = await db.execute(select(User).where(User.id.in_(meeting.user_ids)))
#         users = result.scalars().all()
#
#     db_meeting = Meeting(
#         title=meeting.title,
#         scheduled_at=meeting.scheduled_at,
#         users=users
#     )
#     db.add(db_meeting)
#     await db.commit()
#     return db_meeting
#
#
# @router.get("/{meeting_id}", response_model=MeetingRead)
# async def get_meeting(meeting_id: int, db: AsyncSession = Depends(get_async_db)):
#     meeting = await db.get(Meeting, meeting_id)
#     if not meeting:
#         raise HTTPException(status_code=404, detail="Meeting not found")
#     return meeting
#
#
# @router.delete("/{meeting_id}")
# async def delete_meeting(meeting_id: int, db: AsyncSession = Depends(get_async_db)):
#     meeting = await db.get(Meeting, meeting_id)
#     if not meeting:
#         raise HTTPException(status_code=404, detail="Meeting not found")
#     await db.delete(meeting)
#     await db.commit()
#     return {"message": f"Meeting {meeting_id} deleted"}
#
#
# @router.patch("/{meeting_id}", response_model=MeetingRead)
# async def update_meeting(meeting_id: int, meeting: MeetingUpdate, db: AsyncSession = Depends(get_async_db)):
#     db_meeting = await db.get(Meeting, meeting_id)
#     if not db_meeting:
#         raise HTTPException(status_code=404, detail="Meeting not found")
#
#     update_data = meeting.model_dump(exclude_unset=True)
#
#     if "user_ids" in update_data:
#         user_ids = update_data.pop("user_ids")
#         if user_ids is not None:
#             result = await db.execute(select(User).where(User.id.in_(user_ids)))
#             users = result.scalars().all()
#             db_meeting.users = users
#
#     for field, value in update_data.items():
#         setattr(db_meeting, field, value)
#
#     await db.commit()
#     return db_meeting

# ----------------------------------------------------------------------------------------

@router.get("/")
async def meetings_list(request: Request, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        select(Meeting).options(selectinload(Meeting.users))
    )
    meetings = result.scalars().all()
    return templates.TemplateResponse(
        "meetings/meetings_list.html",
        {"request": request, "meetings": meetings}
    )


@router.get("/create")
async def meeting_create_form(request: Request, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return templates.TemplateResponse(
        "meetings/meeting_create.html",
        {"request": request, "users": users}
    )


@router.post("/create")
async def meeting_create(
        request: Request,
        title: str = Form(...),
        scheduled_at: str = Form(...),
        user_ids: list[int] = Form([]),
        db: AsyncSession = Depends(get_async_db)
):
    scheduled_at_dt = datetime.fromisoformat(scheduled_at)

    result = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = result.scalars().all()

    meeting = Meeting(title=title, scheduled_at=scheduled_at_dt, users=users)
    db.add(meeting)
    await db.commit()
    return templates.TemplateResponse(
        "meetings/meeting_created.html",
        {"request": request, "meeting": meeting, "users": users}
    )


@router.get("/edit/{meeting_id}")
async def meeting_edit_form(request: Request, meeting_id: int, db: AsyncSession = Depends(get_async_db)):
    meeting = await db.get(Meeting, meeting_id)

    result = await db.execute(select(User))
    users = result.scalars().all()

    return templates.TemplateResponse(
        "meetings/meeting_edit.html",
        {"request": request, "meeting": meeting, "users": users}
    )


@router.post("/edit/{meeting_id}")
async def meeting_edit(
        request: Request,
        meeting_id: int,
        title: str = Form(...),
        scheduled_at: str = Form(...),
        user_ids: list[int] = Form([]),
        db: AsyncSession = Depends(get_async_db)
):
    scheduled_at_dt = datetime.fromisoformat(scheduled_at)

    meeting = await db.get(Meeting, meeting_id)

    meeting.title = title
    meeting.scheduled_at = scheduled_at_dt

    result = await db.execute(select(User).where(User.id.in_(user_ids)))
    meeting.users = result.scalars().all()

    await db.commit()
    return RedirectResponse(url="/meetings", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/delete/{meeting_id}")
async def meeting_delete(meeting_id: int, db: AsyncSession = Depends(get_async_db)):
    meeting = await db.get(Meeting, meeting_id)
    await db.delete(meeting)
    await db.commit()
    return HTMLResponse(f"Встреча {meeting.title} удалена")
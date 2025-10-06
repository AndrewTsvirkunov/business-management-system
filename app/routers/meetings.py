from fastapi import APIRouter, Depends, status, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from datetime import datetime

from app.models import Meeting, User
from app.database import get_async_db
from app.config import templates


router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.get("/")
async def meetings_list(request: Request, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        select(Meeting).options(selectinload(Meeting.users))
    )
    meetings = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "meetings/meetings_list.html",
        {"request": request, "meetings": meetings}
    )


@router.get("/create")
async def meeting_create_form(request: Request, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return templates.TemplateResponse(
        request,
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

    conflict = await db.execute(
        select(Meeting)
        .join(Meeting.users)
        .where(Meeting.scheduled_at == scheduled_at_dt, User.id.in_(user_ids))
    )
    conflict_meeting = conflict.scalars().first()
    if conflict_meeting:
        return HTMLResponse(
            content=f"<h3 style='color:red;'>Ошибка:</h3>"
                    f"<p>Один из пользователей уже занят на встрече '{conflict_meeting.title}' в это время</p>",
            status_code=400
        )

    result = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = result.scalars().all()

    meeting = Meeting(title=title, scheduled_at=scheduled_at_dt, users=users)
    db.add(meeting)
    await db.commit()
    return templates.TemplateResponse(
        request,
        "meetings/meeting_created.html",
        {"request": request, "meeting": meeting, "users": users}
    )


@router.get("/edit/{meeting_id}")
async def meeting_edit_form(request: Request, meeting_id: int, db: AsyncSession = Depends(get_async_db)):
    meeting = await db.get(Meeting, meeting_id)

    result = await db.execute(select(User))
    users = result.scalars().all()

    return templates.TemplateResponse(
        request,
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

    conflict = await db.execute(
        select(Meeting)
        .join(Meeting.users)
        .where(Meeting.scheduled_at == scheduled_at_dt, User.id.in_(user_ids))
    )
    conflict_meeting = conflict.scalars().first()
    if conflict_meeting:
        return HTMLResponse(
            content=f"<h3 style='color:red;'>Ошибка:</h3>"
                    f"<p>Один из пользователей уже занят на встрече '{conflict_meeting.title}' в это время</p>",
            status_code=400
        )

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
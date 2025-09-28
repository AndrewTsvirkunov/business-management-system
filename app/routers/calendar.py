from fastapi import APIRouter, Depends
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.shemas import CalendarItem, DayCalendar, MonthCalendar
from app.models import Task, Meeting
from app.database import get_async_db


router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/day/{day}", response_model=DayCalendar)
async def get_day_calendar(day: date, db: AsyncSession = Depends(get_async_db)):
    result_tasks = await db.execute(select(Task).where(func.date(Task.deadline) == day))
    tasks = result_tasks.scalars().all()

    result_meetings = await db.execute(select(Meeting).where(func.date(Meeting.scheduled_at) == day))
    meetings = result_meetings.scalars().all()

    items = [
        CalendarItem(type="task", id=t.id, title=t.title, dating=t.deadline) for t in tasks
    ] + [
        CalendarItem(type="meeting", id=m.id, title=m.title, dating=m.scheduled_at) for m in meetings
    ]
    return DayCalendar(dating=day, items=items)


@router.get("/month/{year}/{month}", response_model=MonthCalendar)
async def get_month_calendar(year: int, month: int, db: AsyncSession = Depends(get_async_db)):
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year+1, 1, 1)
    else:
        end_date = date(year, month+1, 1)

    result_tasks = await db.execute(
        select(Task).where(Task.deadline >= start_date, Task.deadline < end_date)
    )
    tasks = result_tasks.scalars().all()

    result_meetings = await db.execute(
        select(Meeting).where(Meeting.scheduled_at >= start_date, Meeting.scheduled_at < end_date)
    )
    meetings = result_meetings.scalars().all()

    days_map: dict[date, list[CalendarItem]] = {}
    for t in tasks:
        days_map.setdefault(t.deadline.date(), []).append(
            CalendarItem(type="task", id=t.id, title=t.title, dating=t.deadline)
        )
    for m in meetings:
        days_map.setdefault(m.scheduled_at.date(), []).append(
            CalendarItem(type="meeting", id=m.id, title=m.title, dating=m.scheduled_at)
        )

    days = [
        DayCalendar(dating=d, items=items) for d, items in sorted(days_map.items())
    ]

    return MonthCalendar(year=year, month=month, days=days)
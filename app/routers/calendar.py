from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models import Task, Meeting
from app.database import get_async_db
from app.config import templates


router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/day/{day}", response_class=HTMLResponse)
async def day_view(request: Request, day: date, db: AsyncSession = Depends(get_async_db)):
    """
    Отображает календарь задач и встреч за конкретный день.
    Args:
        request (Request): Текущий HTTP-запрос
        day (date): Дата для просмотра
        db (AsyncSession): Асинхронная сессия базы данных
    Returns:
        HTMLResponse: Страница с задачами и встречами за выбранный день
    """
    result_tasks = await db.execute(select(Task).where(func.date(Task.deadline) == day))
    tasks = result_tasks.scalars().all()

    result_meetings = await db.execute(select(Meeting).where(func.date(Meeting.scheduled_at) == day))
    meetings = result_meetings.scalars().all()

    items = [("Задача", t.title) for t in tasks] + [("Встреча", m.title) for m in meetings]

    return templates.TemplateResponse(
        request,
        "calendar/days.html",
        {"request": request, "day": day, "items": items}
    )


@router.get("/month/{year}/{month}")
async def month_view(request: Request, year: int, month: int, db: AsyncSession = Depends(get_async_db)):
    """
    Отображает календарь задач и встреч за указанный месяц.
    Args:
        request (Request): Текущий HTTP-запрос
        year (int): Год для отображения
        month (int): Месяц для отображения
        db (AsyncSession): Асинхронная сессия базы данных
    Returns:
        HTMLResponse: Страница с календарем на месяц и событиями по дням
    """
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year+1, 1, 1)
    else:
        end_date = date(year, month+1, 1)

    days_in_month = (end_date - date(year, month, 1)).days

    result_tasks = await db.execute(
        select(Task).where(Task.deadline >= start_date, Task.deadline < end_date)
    )
    tasks = result_tasks.scalars().all()

    result_meetings = await db.execute(
        select(Meeting).where(Meeting.scheduled_at >= start_date, Meeting.scheduled_at < end_date)
    )
    meetings = result_meetings.scalars().all()

    days: dict[date, list] = {}
    for t in tasks:
        days.setdefault(t.deadline.date(), []).append(("Задача", t.title))
    for m in meetings:
        days.setdefault(m.scheduled_at.date(), []).append(("Встреча", m.title))

    return templates.TemplateResponse(
        request,
        "calendar/months.html",
        {"request": request, "year": year, "month": month, "days": days, "days_in_month": days_in_month, "date": date}
    )
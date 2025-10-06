from fastapi import APIRouter, Depends, status, Request, Form
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
    """
    Отображает список всех встреч.
    Args:
        request (Request): Текущий HTTP-запрос
        db (AsyncSession): Асинхронная сессия базы данных
    Returns:
        HTMLResponse: Страница со списком встреч
    """
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
    """
    Отображает форму для создания новой встречи.
    Args:
        request (Request): Текущий HTTP-запрос
        db (AsyncSession): Асинхронная сессия базы данных
    Returns:
        HTMLResponse: Страница с формой создания встречи
    """
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
    """
    Обрабатывает создание новой встречи.
    Проверяет, чтобы выбранные пользователи не имели конфликтующих встреч
    в то же время, затем сохраняет новую встречу в базу данных.
    Args:
        request (Request): Текущий HTTP-запрос
        title (str): Название встречи
        scheduled_at (str): Дата и время встречи в ISO-формате
        user_ids (list[int]): Список ID пользователей, участвующих во встрече
        db (AsyncSession): Асинхронная сессия базы данных
    Returns:
        HTMLResponse | TemplateResponse: Страница с подтверждением
        или сообщение об ошибке при конфликте расписания
    """
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
    """
    Отображает форму редактирования встречи.
    Args:
        request (Request): Текущий HTTP-запрос
        meeting_id (int): ID редактируемой встречи
        db (AsyncSession): Асинхронная сессия базы данных
    Returns:
        HTMLResponse: Страница с формой редактирования встречи
    """
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
    """
    Обновляет данные встречи по ID.
    Проверяет конфликты по времени для участников и обновляет
    название, время и список пользователей встречи.
    Args:
        request (Request): Текущий HTTP-запрос
        meeting_id (int): ID редактируемой встречи
        title (str): Новое название встречи
        scheduled_at (str): Новое время встречи в ISO-формате
        user_ids (list[int]): Обновлённый список участников
        db (AsyncSession): Асинхронная сессия базы данных
    Returns:
        RedirectResponse | HTMLResponse: Перенаправление на список встреч
        или сообщение об ошибке при конфликте
    """
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
    """
    Удаляет встречу по ID.
    Args:
        meeting_id (int): ID встречи для удаления
        db (AsyncSession): Асинхронная сессия базы данных
    Returns:
        HTMLResponse: Сообщение об успешном удалении встречи
    """
    meeting = await db.get(Meeting, meeting_id)
    await db.delete(meeting)
    await db.commit()
    return HTMLResponse(f"Встреча {meeting.title} удалена")
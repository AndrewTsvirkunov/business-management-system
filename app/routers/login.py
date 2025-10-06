from fastapi import APIRouter, Depends, Request, Response, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import templates
from app.database import get_async_db
from app.auth import authenticate_user, create_access_token


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login_form(request: Request):
    """
    Отображает форму входа в систему.
    Args:
        request (Request): Текущий HTTP-запрос
    Returns:
        HTMLResponse: Страница с формой входа
    """
    return templates.TemplateResponse(request, "login.html", {"request": request})


@router.post("/login")
async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db: AsyncSession = Depends(get_async_db)
):
    """
    Обрабатывает вход пользователя в систему.
    Проверяет учетные данные, создаёт JWT-токен и сохраняет его в cookie.
    Args:
        request (Request): Текущий HTTP-запрос
        username (str): Электронная почта или логин пользователя
        password (str): Пароль пользователя
        db (AsyncSession): Асинхронная сессия базы данных
    Returns:
        RedirectResponse | HTMLResponse:
            - Перенаправление на главную страницу при успешном входе.
            - Сообщение об ошибке при неверных данных
    """
    user = await authenticate_user(db, username, password)
    if not user:
        return HTMLResponse("Неверные данные")

    access_token = create_access_token(data={"sub": user.email})

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=60 * 60 * 24,
        samesite="lax"
    )
    return response


@router.get("/logout")
async def logout(response: Response):
    """
    Выполняет выход пользователя из системы.
    Удаляет cookie с токеном доступа и перенаправляет на страницу входа.
    Args:
        response (Response): HTTP-ответ, в который добавляется удаление cookie
    Returns:
        RedirectResponse: Перенаправление на страницу входа
    """
    response = RedirectResponse(url="/auth/login")
    response.delete_cookie("access_token")
    return response


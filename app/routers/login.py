from fastapi import APIRouter, Depends, Request, Response, Form, Cookie, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import templates
from app.database import get_async_db
from app.auth import authenticate_user, create_access_token


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db: AsyncSession = Depends(get_async_db)
):
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
    response = RedirectResponse(url="/auth/login")
    response.delete_cookie("access_token")
    return response


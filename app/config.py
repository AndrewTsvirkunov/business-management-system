import os
from dotenv import load_dotenv
from datetime import datetime
import pytz
from fastapi.templating import Jinja2Templates


load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

TEST_DB_NAME = os.getenv("TEST_DB_NAME")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
TEST_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}"

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY")


def moscow_now():
    return datetime.now(pytz.timezone("Europe/Moscow"))


def format_moscow(dt: datetime) -> str:
    tz = pytz.timezone("Europe/Moscow")
    return dt.astimezone(tz).strftime("%Y-%m-%d %H:%M")


templates = Jinja2Templates(directory="app/templates")
templates.env.filters["moscowtime"] = format_moscow
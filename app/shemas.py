from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime, date
from typing import Optional


class UserCreate(BaseModel):
    name: str = Field()
    email: EmailStr = Field()
    password: str = Field(min_length=6)
    role: str = Field(default="employee", pattern="^(employee|manager|leader)$")


class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    # teams: list["TeamRead"]

    model_config = ConfigDict(from_attributes=True)


class TeamCreate(BaseModel):
    title: str = Field()
    user_ids: list[int]


class TeamRead(BaseModel):
    id: int
    title: str
    users: list[UserRead]

    model_config = ConfigDict(from_attributes=True)


class TeamUpdate(BaseModel):
    title: Optional[str] = Field(None)
    user_ids: Optional[list[int]] = Field(None)


class TaskCreate(BaseModel):
    title: str = Field()
    description: str = Field()
    status: str = Field(default="open")
    deadline: datetime = Field()
    user_ids: list[int]


class TaskRead(BaseModel):
    id: int
    title: str
    description: str
    status: str
    deadline: datetime
    users: list[UserRead]

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None)
    description: Optional[str] = Field(None)
    status: Optional[str] = Field(None)
    deadline: Optional[datetime] = Field(None)
    user_ids: Optional[list[int]] = Field(None)


class MeetingCreate(BaseModel):
    title: str = Field()
    scheduled_at: datetime = Field()
    user_ids: list[int]


class MeetingRead(BaseModel):
    id: int
    title: str
    scheduled_at: datetime
    users: list[UserRead]

    model_config = ConfigDict(from_attributes=True)


class MeetingUpdate(BaseModel):
    title: Optional[str] = Field(None)
    scheduled_at: Optional[datetime] = Field(None)
    user_ids: Optional[list[int]] = Field(None)


class EvaluationCreate(BaseModel):
    score: int = Field(ge=1, le=5)
    created_at: datetime = Field()
    task_id: int
    user_id: int
    evaluator_id: int


class EvaluationRead(BaseModel):
    id: int
    score: int
    created_at: datetime
    task_id: int
    user_id: int
    evaluator_id: int

    model_config = ConfigDict(from_attributes=True)


class TaskCommentCreate(BaseModel):
    content: str = Field()
    created_at: datetime = Field()
    task_id: int
    user_id: int


class TaskCommentRead(BaseModel):
    id: int
    content: str
    created_at: datetime
    task_id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class CalendarItem(BaseModel):
    type: str
    id: int
    title: str
    dating: datetime


class DayCalendar(BaseModel):
    dating: date
    items: list[CalendarItem]


class MonthCalendar(BaseModel):
    year: int
    month: int
    days: list[DayCalendar]
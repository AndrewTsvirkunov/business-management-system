from sqlalchemy import Integer, String, ForeignKey, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date, datetime, timedelta

from app.database import Base


deadline_date = (datetime.now() + timedelta(days=3)).date()
datetime_meeting = datetime.now() + timedelta(hours=3)


class User(Base):
    __tablename__="users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False, default="employee")
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"))

    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="users")
    teams: Mapped[list["Team"]] = relationship("Team", back_populates="users")
    meetings: Mapped[list["Meeting"]] = relationship("Meeting", back_populates="")


class Team(Base):
    __tablename__="teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)

    users: Mapped[list["User"]] = relationship("User", back_populates="teams")


class Task(Base):
    __tablename__="tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String)
    status: Mapped[int] = mapped_column(String, nullable=False, default="openly")
    deadline: Mapped[date] = mapped_column(Date, default=deadline_date)
    comments: Mapped[str] = mapped_column(String)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    users: Mapped[list["User"]] = relationship("User", back_populates="tasks")


class Meeting(Base):
    __tablename__="meetings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    meeting_date: Mapped[date] = mapped_column(Date, nullable=False, default=datetime.now().date())
    meeting_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime_meeting)

    users: Mapped[list["User"]] = relationship("User", back_populates="meetings")


class Evaluation(Base):
    __tablename__="evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    evaluate: Mapped[int] = mapped_column(Integer)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))


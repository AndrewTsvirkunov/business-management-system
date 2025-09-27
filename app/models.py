from sqlalchemy import Integer, String, ForeignKey, DateTime, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.database import Base


users_teams = Table(
    "users_teams",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("team_id", ForeignKey("teams.id"), primary_key=True)
)

users_tasks = Table(
    "users_tasks",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("task_id", ForeignKey("tasks.id"), primary_key=True)
)

users_meetings = Table(
    "users_meetings",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("meeting_id", ForeignKey("meetings.id"), primary_key=True)
)


class User(Base):
    __tablename__="users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False, default="employee")

    teams: Mapped[list["Team"]] = relationship("Team", secondary="users_teams", back_populates="users", lazy="selectin")
    tasks: Mapped[list["Task"]] = relationship("Task", secondary="users_tasks", back_populates="users", lazy="selectin")
    meetings: Mapped[list["Meeting"]] = relationship("Meeting", secondary="users_meetings", back_populates="users", lazy="selectin")
    evaluations: Mapped[list["Evaluation"]] = relationship("Evaluation", foreign_keys="Evaluation.user_id", back_populates="user", lazy="selectin")
    evaluations_given: Mapped[list["Evaluation"]] = relationship("Evaluation", foreign_keys="Evaluation.evaluator_id", back_populates="evaluator", lazy="selectin")


class Team(Base):
    __tablename__="teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    users: Mapped[list["User"]] = relationship("User", secondary="users_teams", back_populates="teams", lazy="selectin")


class Task(Base):
    __tablename__="tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="open")
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    users: Mapped[list["User"]] = relationship("User", secondary="users_tasks", back_populates="tasks")
    evaluations: Mapped[list["Evaluation"]] = relationship("Evaluation", back_populates="task")
    comments: Mapped[list["TaskComment"]] = relationship("TaskComment", back_populates="task")


class TaskComment(Base):
    __tablename__="task_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    task: Mapped["Task"] = relationship("Task", back_populates="comments")
    user: Mapped["User"] = relationship("User")


class Meeting(Base):
    __tablename__="meetings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    users: Mapped[list["User"]] = relationship("User", secondary="users_meetings", back_populates="meetings")


class Evaluation(Base):
    __tablename__="evaluations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now())
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    evaluator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    task: Mapped["Task"] = relationship("Task", back_populates="evaluations")
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="evaluations")
    evaluator: Mapped["User"] = relationship("User", foreign_keys=[evaluator_id], back_populates="evaluations_given")


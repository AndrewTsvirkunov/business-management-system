@router.post("/", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
async def create_team(team: TeamCreate, db: AsyncSession = Depends(get_async_db)):
    users = []
    if team.user_ids:
        result = await db.execute(select(User).where(User.id.in_(team.user_ids)))
        users = result.scalars().all()
    db_team = Team(
        title=team.title,
        users=users
    )
    db.add(db_team)
    await db.commit()
    return db_team


@router.get("/{team_id}", response_model=TeamRead)
async def get_team(team_id: int, db: AsyncSession = Depends(get_async_db)):
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.delete("/{team_id}")
async def delete_team(team_id: int, db: AsyncSession = Depends(get_async_db)):
    team = await db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    await db.delete(team)
    await db.commit()
    return {"message": f"Team {team.title} deleted"}


@router.patch("/{team_id}", response_model=TeamRead)
async def update_team(team_id: int, team: TeamUpdate, db: AsyncSession = Depends(get_async_db)):
    db_team = await db.get(Team, team_id)
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")

    update_data = team.model_dump(exclude_unset=True)

    if "user_ids" in update_data:
        user_ids = update_data.pop("user_ids")
        if user_ids is not None:
            result = await db.execute(select(User).where(User.id.in_(user_ids)))
            users = result.scalars().all()
            db_team.users = users

    for field, value in update_data.items():
        setattr(db_team, field, value)

    await db.commit()
    return db_team


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, db:AsyncSession = Depends(get_async_db)):
    users = []
    if task.user_ids:
        result = await db.execute(select(User).where(User.id.in_(task.user_ids)))
        users = result.scalars().all()

    db_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        deadline=task.deadline,
        users=users
    )
    db.add(db_task)
    await db.commit()
    return db_task


@router.get("/{task_id}", response_model=TaskRead)
async def get_task_info(task_id: int, db: AsyncSession = Depends(get_async_db)):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", response_model=TaskRead)
async def delete_task(task_id: int, db: AsyncSession = Depends(get_async_db)):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)
    await db.commit()
    return {"message": f"Task {task_id} deleted"}


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(task_id: int, task: TaskUpdate, db: AsyncSession = Depends(get_async_db)):
    db_task = await db.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task.model_dump(exclude_unset=True)

    if "user_ids" in update_data:
        user_ids = update_data.pop("user_ids")
        if user_ids is not None:
            result = await db.execute(select(User).where(User.id.in_(user_ids)))
            users = result.scalars().all()
            db_task.users = users

    for field, value in update_data.items():
        setattr(db_task, field, value)

    await db.commit()
    return db_task


@router.post("/", response_model=MeetingRead, status_code=status.HTTP_201_CREATED)
async def create_meeting(meeting: MeetingCreate, db: AsyncSession = Depends(get_async_db)):
    users = []
    if meeting.user_ids:
        result = await db.execute(select(User).where(User.id.in_(meeting.user_ids)))
        users = result.scalars().all()

    db_meeting = Meeting(
        title=meeting.title,
        scheduled_at=meeting.scheduled_at,
        users=users
    )
    db.add(db_meeting)
    await db.commit()
    return db_meeting


@router.get("/{meeting_id}", response_model=MeetingRead)
async def get_meeting(meeting_id: int, db: AsyncSession = Depends(get_async_db)):
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.delete("/{meeting_id}")
async def delete_meeting(meeting_id: int, db: AsyncSession = Depends(get_async_db)):
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    await db.delete(meeting)
    await db.commit()
    return {"message": f"Meeting {meeting_id} deleted"}


@router.patch("/{meeting_id}", response_model=MeetingRead)
async def update_meeting(meeting_id: int, meeting: MeetingUpdate, db: AsyncSession = Depends(get_async_db)):
    db_meeting = await db.get(Meeting, meeting_id)
    if not db_meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    update_data = meeting.model_dump(exclude_unset=True)

    if "user_ids" in update_data:
        user_ids = update_data.pop("user_ids")
        if user_ids is not None:
            result = await db.execute(select(User).where(User.id.in_(user_ids)))
            users = result.scalars().all()
            db_meeting.users = users

    for field, value in update_data.items():
        setattr(db_meeting, field, value)

    await db.commit()
    return db_meeting


@router.post("/", response_model=EvaluationRead, status_code=status.HTTP_201_CREATED)
async def create_evaluation(evaluation: EvaluationCreate, db: AsyncSession = Depends(get_async_db)):
    task = await db.get(Task, evaluation.task_id)
    user = await db.get(User, evaluation.user_id)
    evaluator = await db.get(User, evaluation.evaluator_id)

    if not task or not user or not evaluator:
        raise HTTPException(status_code=404, detail="Task or user or evaluator not found")

    db_evaluation = Evaluation(
        score=evaluation.score,
        created_at=evaluation.created_at,
        task_id=evaluation.task_id,
        user_id=evaluation.user_id,
        evaluator_id=evaluation.evaluator_id
    )
    db.add(db_evaluation)
    await db.commit()
    return db_evaluation


@router.get("/{user_id}", response_model=list[EvaluationRead])
async def get_evaluation(user_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Evaluation).where(Evaluation.user_id == user_id))
    evaluation = result.scalars().all()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return evaluation


@router.delete("/{user_id}")
async def delete_evaluation(evaluation_id: int, db: AsyncSession = Depends(get_async_db)):
    evaluation = await db.get(Evaluation, evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    await db.delete(evaluation)
    await db.commit()
    return {"message": f"Evaluate {evaluation_id} for user {evaluation.user_id} deleted"}


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


@router.post("/", response_model=TaskCommentRead, status_code=status.HTTP_201_CREATED)
async def create_task_comment(comment: TaskCommentCreate, db: AsyncSession = Depends(get_async_db)):
    task = await db.get(Task, comment.task_id)
    user = await db.get(User, comment.user_id)

    if not task or not user:
        raise HTTPException(status_code=404, detail="Task or user not found")

    db_comment = TaskComment(
        content=comment.content,
        created_at=comment.created_at,
        task_id=comment.task_id,
        user_id=comment.user_id
    )
    db.add(db_comment)
    await db.commit()
    return db_comment


@router.get("/{task_id}", response_model=list[TaskCommentRead])
async def get_task_comments(task_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(TaskComment).where(TaskComment.task_id == task_id))
    comments = result.scalars().all()
    if not comments:
        raise HTTPException(status_code=404, detail="Task not found")
    return comments
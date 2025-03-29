# crud/workout.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.workout import (
    PerformedExercise,
    PerformedSet,
    PerformedWorkout,
    WorkoutTemplate,
    WorkoutExercise,
    ExerciseSet,
)
from schemas.workout import ExerciseStart, SetComplete, SetStart, WorkoutTemplateCreate
from typing import List, Optional
import isodate
from fastapi import HTTPException, status
from errors.websocket import WebSocketError
from sqlalchemy import select, and_, func
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta


async def create_workout_template(
    db: AsyncSession, user_id: int, template_data: WorkoutTemplateCreate
) -> WorkoutTemplate:
    # Create main template
    db_template = WorkoutTemplate(
        user_id=user_id, name=template_data.name, description=template_data.description
    )

    db.add(db_template)
    await db.commit()
    await db.refresh(db_template)

    # Add exercises and sets
    for exercise in template_data.exercises:
        db_exercise = WorkoutExercise(
            template_id=db_template.id,
            activity_id=exercise.activity_id,
            order=exercise.order,
            rest_between_sets=isodate.parse_duration(exercise.rest_between_sets),
            notes=exercise.notes,
        )
        db.add(db_exercise)
        await db.commit()
        await db.refresh(db_exercise)

        for set_data in exercise.sets:
            db_set = ExerciseSet(
                exercise_id=db_exercise.id,
                set_number=set_data.set_number,
                set_type=set_data.set_type,
                parameters=set_data.parameters,
            )
            db.add(db_set)

    await db.commit()
    return db_template


async def get_user_templates(
    db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
) -> List[WorkoutTemplate]:
    result = await db.execute(
        select(WorkoutTemplate)
        .where(WorkoutTemplate.user_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_template_by_id(
    db: AsyncSession, template_id: int, user_id: int
) -> Optional[WorkoutTemplate]:
    result = await db.execute(
        select(WorkoutTemplate).where(
            (WorkoutTemplate.id == template_id) & (WorkoutTemplate.user_id == user_id)
        )
    )
    return result.scalar_one_or_none()


async def update_workout_template(
    db: AsyncSession,
    user_id: int,
    template_id: int,
    template_data: WorkoutTemplateCreate,
) -> WorkoutTemplate:
    # Get existing template
    existing_template = await get_template_by_id(db, template_id, user_id)
    if not existing_template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Update top-level fields
    existing_template.name = template_data.name
    existing_template.description = template_data.description

    # Clear existing exercises (cascade delete sets)
    existing_template.exercises = []

    # Add new exercises
    for exercise in template_data.exercises:
        db_exercise = WorkoutExercise(
            template_id=existing_template.id,
            activity_id=exercise.activity_id,
            order=exercise.order,
            rest_between_sets=isodate.parse_duration(exercise.rest_between_sets),
            notes=exercise.notes,
        )

        # Add sets
        db_exercise.sets = [
            ExerciseSet(
                set_number=set_data.set_number,
                set_type=set_data.set_type,
                parameters=set_data.parameters,
            )
            for set_data in exercise.sets
        ]

        db.add(db_exercise)

    await db.commit()
    await db.refresh(existing_template)
    return existing_template


async def delete_workout_template(
    db: AsyncSession, user_id: int, template_id: int
) -> None:
    template = await get_template_by_id(db, template_id, user_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    await db.delete(template)
    await db.commit()


async def get_set(db: AsyncSession, set_id: int, user_id: int) -> PerformedSet:
    result = await db.execute(
        select(PerformedSet)
        .join(PerformedExercise)
        .join(PerformedWorkout)
        .where(and_(PerformedSet.id == set_id, PerformedWorkout.user_id == user_id))
        .options(joinedload(PerformedSet.exercise))
    )
    set_record = result.scalar_one_or_none()

    if set_record := result.scalar_one_or_none():
        return set_record
    else:
        raise HTTPException(status_code=404, detail="Set not found")


async def calculate_rest_periods(db: AsyncSession, set_record: PerformedSet) -> None:
    # Get previous set in the same exercise
    result = await db.execute(
        select(PerformedSet)
        .where(
            and_(
                PerformedSet.exercise_id == set_record.exercise_id,
                PerformedSet.set_number < set_record.set_number,
            )
        )
        .order_by(PerformedSet.set_number.desc())
        .limit(1)
    )
    previous_set = result.scalar_one_or_none()

    rest_duration = timedelta(0)
    if previous_set and previous_set.end_time:
        rest_duration = set_record.start_time - previous_set.end_time

    # Update exercise's rest periods
    exercise = set_record.exercise
    rest_periods = exercise.rest_periods or {"between_sets": []}

    if len(rest_periods["between_sets"]) >= set_record.set_number - 1:
        # Update existing entry
        rest_periods["between_sets"][
            set_record.set_number - 2
        ] = rest_duration.total_seconds()
    else:
        # Add new entry
        rest_periods["between_sets"].append(rest_duration.total_seconds())

    exercise.rest_periods = rest_periods
    await db.commit()


async def handle_exercise_start(
    db: AsyncSession, workout: PerformedWorkout, data: dict
) -> None:
    exercise_data = ExerciseStart(**data.get("data", {}))

    # Create new exercise record
    exercise = PerformedExercise(
        workout_id=workout.id,
        activity_id=exercise_data.activity_id,
        start_time=datetime.now(),
        rest_periods={"between_sets": []},
    )

    db.add(exercise)
    await db.commit()

    # Add to workout structure
    workout.exercises.append(exercise)
    await db.refresh(workout)


async def handle_set_start(
    db: AsyncSession, workout: PerformedWorkout, data: dict
) -> None:
    set_data = SetStart(**data.get("data", {}))

    # Get current exercise
    if not workout.exercises or workout.exercises[-1].end_time is not None:
        raise WebSocketError(
            code=status.WS_1003_UNSUPPORTED_DATA, reason="No active exercise"
        )

    current_exercise = workout.exercises[-1]

    # Create new set
    set_number = len(current_exercise.sets) + 1
    set_record = PerformedSet(
        exercise_id=current_exercise.id,
        set_number=set_number,
        weight=set_data.weight,
        reps=set_data.reps,
        is_warmup=set_data.is_warmup,
        start_time=datetime.now(),
    )

    db.add(set_record)
    await db.commit()
    await db.refresh(current_exercise)


async def handle_set_complete(
    db: AsyncSession, workout: PerformedWorkout, data: dict
) -> None:
    set_data = SetComplete(**data.get("data", {}))

    # Get latest set
    if not workout.exercises:
        raise WebSocketError(
            code=status.WS_1003_UNSUPPORTED_DATA, reason="No exercises started"
        )

    current_exercise = workout.exercises[-1]
    if not current_exercise.sets:
        raise WebSocketError(
            code=status.WS_1003_UNSUPPORTED_DATA, reason="No sets started"
        )

    set_record = current_exercise.sets[-1]
    set_record.end_time = datetime.now()
    set_record.rpe = set_data.rpe
    set_record.notes = set_data.notes

    await calculate_rest_periods(db, set_record)
    await db.commit()

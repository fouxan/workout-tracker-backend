# crud/workout.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.workout import WorkoutTemplate, WorkoutExercise, ExerciseSet
from schemas.workout import WorkoutTemplateCreate
from typing import List, Optional
import isodate
from fastapi import HTTPException


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


# Add update and delete operations similarly
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

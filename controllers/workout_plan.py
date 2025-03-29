# crud/plan.py
from sqlalchemy import select, and_
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models.workout_plan import WorkoutPlan, PlanDay, ScheduledWorkout
from schemas.workout_plan import WorkoutPlanCreate
from typing import List, Optional
from sqlalchemy import update


async def create_workout_plan(
    db: AsyncSession,
    user_id: int,
    plan_data: WorkoutPlanCreate,
    activate_now: bool = False,
) -> WorkoutPlan:
    # Deactivate existing plans if activating new one
    if activate_now:
        await db.execute(
            update(WorkoutPlan)
            .where(WorkoutPlan.user_id == user_id)
            .values(is_active=False)
        )

    # Create new plan
    db_plan = WorkoutPlan(
        user_id=user_id,
        name=plan_data.name,
        description=plan_data.description,
        start_date=plan_data.start_date,
        end_date=plan_data.end_date,
        is_active=activate_now,
    )

    # Add plan and relationships
    db.add(db_plan)
    await db.commit()
    await db.refresh(db_plan)

    # Clear existing days (if any) and add new ones
    db_plan.days = []
    for day in plan_data.days:
        db_day = PlanDay(
            day_number=day.day_number,
            focus_area=day.focus_area,
            notes=day.notes,
            plan_id=db_plan.id,
        )
        db_day.scheduled_workouts = [
            ScheduledWorkout(
                template_id=workout.template_id, scheduled_time=workout.scheduled_time
            )
            for workout in day.workouts
        ]
        db.add(db_day)

    await db.commit()
    return db_plan


async def update_workout_plan(
    db: AsyncSession, user_id: int, plan_id: int, plan_data: WorkoutPlanCreate
) -> WorkoutPlan:
    plan = await get_plan_by_id(db, plan_id, user_id)
    if not plan:
        raise HTTPException(404, detail="Plan not found")

    # Update plan fields
    plan.name = plan_data.name
    plan.description = plan_data.description
    plan.start_date = plan_data.start_date
    plan.end_date = plan_data.end_date

    # Replace days and workouts
    plan.days = []
    for day in plan_data.days:
        db_day = PlanDay(
            day_number=day.day_number,
            focus_area=day.focus_area,
            notes=day.notes,
            plan_id=plan_id,
        )
        db_day.scheduled_workouts = [
            ScheduledWorkout(
                template_id=workout.template_id, scheduled_time=workout.scheduled_time
            )
            for workout in day.workouts
        ]
        db.add(db_day)

    await db.commit()
    await db.refresh(plan)
    return plan


async def activate_plan(db: AsyncSession, user_id: int, plan_id: int) -> WorkoutPlan:
    # Deactivate all plans
    await db.execute(
        update(WorkoutPlan)
        .where(WorkoutPlan.user_id == user_id)
        .values(is_active=False)
    )

    # Activate target plan
    plan = await get_plan_by_id(db, plan_id, user_id)
    if not plan:
        raise HTTPException(404, detail="Plan not found")

    plan.is_active = True
    await db.commit()
    await db.refresh(plan)
    return plan


async def delete_workout_plan(db: AsyncSession, user_id: int, plan_id: int) -> None:
    plan = await get_plan_by_id(db, plan_id, user_id)
    if not plan:
        raise HTTPException(404, detail="Plan not found")

    await db.delete(plan)
    await db.commit()


async def get_plan_by_id(
    db: AsyncSession, plan_id: int, user_id: int
) -> Optional[WorkoutPlan]:
    result = await db.execute(
        select(WorkoutPlan).where(
            and_(WorkoutPlan.id == plan_id, WorkoutPlan.user_id == user_id)
        )
    )
    return result.scalar_one_or_none()


async def get_user_plans(
    db: AsyncSession, user_id: int, active_only: bool = False
) -> List[WorkoutPlan]:
    query = select(WorkoutPlan).where(WorkoutPlan.user_id == user_id)

    if active_only:
        query = query.where(WorkoutPlan.is_active == True)

    result = await db.execute(query)
    return result.scalars().all()

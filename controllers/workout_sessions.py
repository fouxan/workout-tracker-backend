from sqlalchemy import select, UUID
from sqlalchemy import delete
from sqlalchemy import update
from sqlalchemy.orm import selectinload
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import and_, func
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from models.activity import ActivityRecords
from models.workout import (
    ActivitySets,
    WorkoutSessions,
    WorkoutSessionActivities,
    WorkoutTemplateActivities,
)
from services.calories import get_calories_burnt


async def _get_next_activity_order(session, session_id: UUID) -> int:
    """Get next available order position for new activity"""
    last_order = await session.scalar(
        select(func.max(WorkoutSessionActivities.order)).filter_by(
            session_id=session_id
        )
    )
    return (last_order or 0) + 1


async def start_session_from_template(db, template_id: UUID, user_id: UUID):
    # takes in a template_id and starts a session by bulk populating session_activities and activity_sets if they exist in the template
    # returns the session object

    # Create a new session object
    async with db.AsyncSession() as session:
        new_session = WorkoutSessions(
            user_id=user_id,
            template_id=template_id,
            started_at=datetime.now(),
        )
        session.add(new_session)
        await session.flush()

        template_activities = await session.execute(
            select(WorkoutTemplateActivities).filter_by(template_id=template_id)
        )

        for ta in template_activities.scalars():
            sa = WorkoutSessionActivities(
                session_id=new_session.id, activity_id=ta.activity_id, order=ta.order
            )
            session.add(sa)
            await session.flush()

            # Copy sets
            sets = await session.execute(
                select(ActivitySets).filter_by(template_activity_id=ta.id)
            )
            for s in sets.scalars():
                session.add(
                    ActivitySets(
                        session_activity_id=sa.id,
                        set_number=s.set_number,
                        reps=s.reps,
                        weight=s.weight,
                        duration=s.duration,
                        rpe=s.rpe,
                        pace=s.pace,
                        heart_rate=s.heart_rate,
                        is_active=s.is_active,
                        notes=s.notes,
                        is_warmup=s.is_warmup,
                        is_cooldown=s.is_cooldown,
                        rest_after_set=s.rest_after_set,
                        set_type=s.set_type,
                    )
                )

        await session.commit()
        return {"session_id": new_session.id}


async def start_empty_session(db, user_id: UUID, name: Optional[str] = None) -> dict:
    """
    Creates a session with no template reference
    Steps:
    1. Create session with 'draft' status
    2. Return immediate session ID for real-time updates
    """
    async with db.AsyncSession() as session:
        new_session = WorkoutSessions(
            user_id=user_id,
            status="draft",
            name=name or f"Workout {datetime.now().strftime('%m/%d')}",
            started_at=datetime.now(),
        )
        session.add(new_session)
        await session.commit()
        return {"session_id": new_session.id, "status": "draft"}


def start_activity_in_session():
    pass


def discard_activity_in_session():
    pass


def complete_activity_in_session():
    pass


async def add_activity_to_session(
    db, session_id: UUID, activity_id: UUID, set_count: int = 3
) -> dict:
    """
    Adds an activity to live session with default sets
    Steps:
    1. Verify session exists and is active/draft
    2. Create session activity record
    3. Initialize empty sets
    """
    async with db.AsyncSession() as session:
        # Validate session state
        workout = await session.get(WorkoutSessions, session_id)
        if not workout:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
        if workout.status not in ("draft", "active"):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Session is locked")

        # Create activity
        new_activity = WorkoutSessionActivities(
            session_id=session_id,
            activity_id=activity_id,
            order=await _get_next_activity_order(session, session_id),
        )
        session.add(new_activity)
        await session.flush()

        # Add default sets

        await session.commit()
        return {"activity_id": new_activity.id}


def remove_activity_from_session():
    pass


async def start_set_in_session(db, set_id: UUID) -> dict:
    """
    Marks a set as active with timestamp
    Steps:
    1. Validate set exists
    2. Ensure no other active sets in session
    3. Update set and session state
    """
    async with db.AsyncSession() as session:
        # Lock set for update
        active_set = await session.execute(
            select(ActivitySets).filter_by(id=set_id).with_for_update()
        )
        active_set = active_set.scalar_one_or_none()

        if not active_set:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Set not found")

        # Verify session state
        session_obj = await session.get(
            WorkoutSessions, active_set.session_activity.session_id
        )
        if session_obj.status != "active":
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Session not active")

        # Deactivate other sets
        await session.execute(
            update(ActivitySets)
            .where(
                ActivitySets.session_activity_id == active_set.session_activity_id,
                ActivitySets.is_active == True,
            )
            .values(is_active=False)
        )

        # Activate current set
        active_set.is_active = True
        active_set.started_at = datetime.now()
        session_obj.status = "active"

        await session.commit()
        return {"status": "active"}


async def complete_set_in_session(
    db, set_id: UUID, reps: Optional[int] = None, weight: Optional[float] = None
) -> dict:
    """
    Finalizes set data and calculates metrics
    Steps:
    1. Validate set is active
    2. Update performance metrics
    3. Calculate rest period if applicable
    """
    async with db.AsyncSession() as session:
        set_record = await session.get(ActivitySets, set_id)
        if not set_record:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Set not found")

        if not set_record.is_active:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Set not started")

        # Update metrics
        set_record.reps = reps
        set_record.weight = weight
        set_record.ended_at = datetime.now()
        set_record.is_active = False
        set_record.duration = (
            set_record.ended_at - set_record.started_at
        ).total_seconds()

        # Auto-calculate rest period
        next_set = await session.execute(
            select(ActivitySets).filter_by(
                session_activity_id=set_record.session_activity_id,
                set_number=set_record.set_number + 1,
            )
        )
        if next_set := next_set.scalar_one_or_none():
            next_set.rest_after_set = min(
                300,  # Cap at 5 minutes
                int(set_record.duration * 0.3),  # 30% of set duration
            )

        await session.commit()
        return {"status": "completed"}


def discard_set_in_session():
    pass


def add_set_to_session(db, session_activity_id: UUID, set_data: list):
    with db.AsyncSession as session:
        for i in range(len(set_data)):
            session.add(
                ActivitySets(
                    session_activity_id=session_activity_id,
                    reps=set_data[i].get("reps"),
                    weight=set_data[i].get("weight"),
                    duration=set_data[i].get("duration"),
                    rpe=set_data[i].get("rpe"),
                    pace=set_data[i].get("pace"),
                    heart_rate=set_data[i].get("heart_rate"),
                    is_active=False,
                    notes=set_data[i].get("notes"),
                    rest_after_set=set_data[i].get("rest_after_set"),
                    set_type=set_data[i].get("set_type"),
                    set_number=i,
                    is_warmup=(i == 0),  # First set as warmup by default
                    is_cooldown=(i == len(set_data) - 1),  # Last set as cooldown
                )
            )


async def discard_session(db, session_id: UUID):
    async with db.AsyncSession() as session:
        workout = await session.get(WorkoutSessions, session_id)
        if not workout:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )
        # Mark as discarded
        workout.status = "discarded"
        workout.ended_at = datetime.now()
        await session.commit()


async def finish_session(db, session_id: UUID, user_id: UUID):
    async with db.AsyncSession() as session:
        # Mark as finished
        workout_session = await session.get(WorkoutSessions, session_id)
        if not workout_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )
        workout_session.status = "finished"
        workout_session.ended_at = datetime.now()

        # Calculate totals - calories burnt

        total_calories = get_calories_burnt(workout_session)
        workout_session.calories_burnt = total_calories

        workout_session_activities = await session.execute(
            select(WorkoutSessionActivities)
            .where(WorkoutSessionActivities.session_id == workout_session.id)
            .options(joinedload(WorkoutSessionActivities.sets))
        )

        # Update activity records table
        for activity in workout_session_activities:

            if record := session.execute(
                select(ActivityRecords).where(
                    ActivityRecords.activity_id == activity.activity_id,
                )
            ):
                record.times_performed += 1
                record.max_reps = max(
                    record.max_reps,
                    max(s.reps for s in activity.sets if s.reps is not None),
                )
                record.max_duration = max(
                    record.max_duration,
                    max(s.duration for s in activity.sets if s.duration is not None),
                )
                record.max_rpe = max(
                    record.max_rpe,
                    max(s.rpe for s in activity.sets if s.rpe is not None),
                )
                record.max_heart_rate = max(
                    record.max_heart_rate,
                    max(
                        s.heart_rate for s in activity.sets if s.heart_rate is not None
                    ),
                )
                record.max_pace = max(
                    record.max_pace,
                    max(s.pace for s in activity.sets if s.pace is not None),
                )
                record.recorded_at = datetime.now().isoformat()
                record.max_weight = max(
                    record.max_weight,
                    max(s.weight for s in activity.sets if s.weight is not None),
                )
            else:
                record = ActivityRecords(
                    activity_id=activity.activity_id,
                    user_id=user_id,
                    times_performed=1,
                    max_reps=max(s.reps for s in activity.sets if s.reps is not None),
                    max_duration=max(
                        s.duration for s in activity.sets if s.duration is not None
                    ),
                    max_rpe=max(s.rpe for s in activity.sets if s.rpe is not None),
                    max_heart_rate=max(
                        s.heart_rate for s in activity.sets if s.heart_rate is not None
                    ),
                    max_pace=max(s.pace for s in activity.sets if s.pace is not None),
                    recorded_at=datetime.now().isoformat(),
                    max_weight=max(
                        s.weight for s in activity.sets if s.weight is not None
                    ),
                )
                session.add(record)

        await session.commit()


def get_session():
    pass


async def get_sessions(
    db, user_id: UUID, status_filter: Optional[str] = None, limit: int = 50
) -> List[dict]:
    """
    Retrieves session summaries with pagination
    Steps:
    1. Apply status filter if provided
    2. Load basic session data
    3. Include activity count
    """
    query = (
        select(WorkoutSessions)
        .filter_by(user_id=user_id)
        .options(selectinload(WorkoutSessions.activities))
        .order_by(WorkoutSessions.started_at.desc())
        .limit(limit)
    )

    if status_filter:
        query = query.filter_by(status=status_filter)

    async with db.AsyncSession() as session:
        result = await session.execute(query)
        return [
            {
                "id": s.id,
                "name": s.name,
                "started_at": s.started_at,
                "activity_count": len(s.activities),
                "status": s.status,
            }
            for s in result.scalars()
        ]


async def get_live_session(db, session_id: str):
    result = await db.execute(
        select(WorkoutSessions)
        .options(
            selectinload(WorkoutSessions.activities).selectinload(
                WorkoutSessionActivities.sets
            )
        )
        .filter(WorkoutSessions.id == session_id)
    )
    return result.scalars().first()


async def modify_template_session(db, session_id: UUID) -> dict:
    """
    Detaches session from its template
    Steps:
    1. Verify session has template
    2. Nullify template reference
    3. Keep existing activities
    """
    async with db.AsyncSession() as session:
        workout = await session.get(WorkoutSessions, session_id)
        if not workout:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
        if not workout.template_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "No template linked")

        workout.template_id = None
        workout.status = "active"  # Force active state
        await session.commit()
        return {"status": "detached"}


async def delete_discarded_sessions(db, older_than_days: int = 30) -> dict:
    """
    Hard deletes discarded sessions past retention period
    Steps:
    1. Query sessions meeting criteria
    2. Cascade delete all related records
    """
    async with db.AsyncSession() as session:
        cutoff = datetime.now() - timedelta(days=older_than_days)
        result = await session.execute(
            delete(WorkoutSessions)
            .where(
                and_(
                    WorkoutSessions.status == "discarded",
                    WorkoutSessions.ended_at < cutoff,
                )
            )
            .returning(WorkoutSessions.id)
        )
        await session.commit()
        return {"deleted_count": len(result.all())}

# routers/workout.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models.workout import PerformedExercise, PerformedWorkout
from schemas.workout import *
from controllers.workout import *
from services.db import get_db
from services.auth import get_current_user
from models.auth import User
from fastapi import WebSocket, WebSocketDisconnect
from services.realtime import ConnectionManager
from services.websocket import authenticate_websocket

manager = ConnectionManager()


router = APIRouter(prefix="/workouts/templates", tags=["workout_templates"])


@router.post(
    "/", response_model=WorkoutTemplateResponse, status_code=status.HTTP_201_CREATED
)
async def create_template(
    template_data: WorkoutTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await create_workout_template(db, current_user.id, template_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@router.get("/", response_model=List[WorkoutTemplateResponse])
async def list_templates(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_user_templates(db, current_user.id, skip, limit)


@router.get("/{template_id}", response_model=WorkoutTemplateResponse)
async def get_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    template = await get_template_by_id(db, template_id, current_user.id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )
    return template


@router.put("/{template_id}", response_model=WorkoutTemplateResponse)
async def update_template(
    template_id: int,
    template_data: WorkoutTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await update_workout_template(
            db, current_user.id, template_id, template_data
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating template: {str(e)}"
        ) from e


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        await delete_workout_template(db, current_user.id, template_id)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting template: {str(e)}"
        ) from e


@router.post("/active", response_model=WorkoutResponse, status_code=201)
async def start_workout(
    workout_data: WorkoutStart,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check for existing active workout
    active_workout = await get_active_workout(db, current_user.id)
    if active_workout:
        raise HTTPException(400, "Finish current workout first")

    # Create new workout
    workout = PerformedWorkout(
        user_id=current_user.id, template_id=workout_data.template_id
    )
    db.add(workout)
    await db.commit()
    return workout


@router.get("/active", response_model=WorkoutResponse)
async def get_active_workout(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    workout = await get_active_workout(db, current_user.id)
    if not workout:
        raise HTTPException(404, "No active workout")
    return workout


@router.post("/active/complete", response_model=WorkoutResponse)
async def complete_workout(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    workout = await get_active_workout(db, current_user.id)
    workout.status = "completed"
    workout.end_time = datetime.now()

    # Calculate metrics
    # workout.performance_metrics = await calculate_metrics(workout)

    await db.commit()
    return workout


@router.websocket("/active/ws")
async def workout_websocket(
    websocket: WebSocket, token: str, db: AsyncSession = Depends(get_db)
):
    user = await authenticate_websocket(token, db)
    await manager.connect(websocket)

    try:
        active_workout = await get_active_workout(db, user.id)
        if not active_workout:
            await websocket.close(code=1008)
            return

        while True:
            data = await websocket.receive_json()
            update_type = data.get("type")

            # Handle different update types
            if update_type == "set_start":
                await handle_set_start(db, active_workout, data)
            elif update_type == "set_complete":
                await handle_set_complete(db, active_workout, data)
            elif update_type == "exercise_start":
                await handle_exercise_start(db, active_workout, data)

            # Broadcast update to all connected clients
            await manager.broadcast(
                {"type": update_type, "data": data, "userId": user.id}
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.post("/active/exercises", status_code=201)
async def start_exercise(
    exercise_data: ExerciseStart,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workout = await get_active_workout(db, current_user.id)
    exercise = PerformedExercise(
        workout_id=workout.id,
        activity_id=exercise_data.activity_id,
        start_time=datetime.now(),
    )
    db.add(exercise)
    await db.commit()
    return exercise


@router.put("/active/sets/{set_id}/start")
async def start_set(
    set_id: int,
    set_data: SetStart,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    set_record = await get_set(db, set_id, current_user.id)
    set_record.start_time = datetime.now()
    set_record.weight = set_data.weight
    set_record.reps = set_data.reps
    set_record.is_warmup = set_data.is_warmup
    await db.commit()
    return set_record


@router.put("/active/sets/{set_id}/complete")
async def complete_set(
    set_id: int,
    set_data: SetComplete,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    set_record = await get_set(db, set_id, current_user.id)
    set_record.end_time = datetime.now()
    set_record.rpe = set_data.rpe
    set_record.notes = set_data.notes

    # Calculate rest period
    await calculate_rest_periods(db, set_record)

    await db.commit()
    return set_record

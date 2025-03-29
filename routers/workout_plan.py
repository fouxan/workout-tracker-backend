# routers/plan.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.workout_plan import *
from controllers.workout_plan import *
from services.db import get_db
from services.auth import get_current_user
from models.auth import User


router = APIRouter(prefix="/plans", tags=["workout_plans"])


@router.get("/", response_model=List[WorkoutPlanResponse])
async def list_plans(
    active: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_user_plans(db, current_user.id, active_only=active)


@router.get("/{plan_id}", response_model=WorkoutPlanResponse)
async def get_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = await get_plan_by_id(db, plan_id, current_user.id)
    if not plan:
        raise HTTPException(404, detail="Plan not found")
    return plan


@router.post("/", response_model=WorkoutPlanResponse, status_code=201)
async def create_plan(
    plan_data: WorkoutPlanCreate,
    activate_now: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await create_workout_plan(db, current_user.id, plan_data, activate_now)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, detail=str(e)) from e


@router.put("/{plan_id}", response_model=WorkoutPlanResponse)
async def update_plan(
    plan_id: int,
    plan_data: WorkoutPlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await update_workout_plan(db, current_user.id, plan_id, plan_data)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, detail=str(e)) from e


@router.patch("/{plan_id}/activate", response_model=WorkoutPlanResponse)
async def activate_plan_endpoint(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await activate_plan(db, current_user.id, plan_id)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, detail=str(e)) from e


@router.patch("/{plan_id}/deactivate", response_model=WorkoutPlanResponse)
async def deactivate_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = await get_plan_by_id(db, plan_id, current_user.id)
    if not plan:
        raise HTTPException(404, detail="Plan not found")

    plan.is_active = False
    await db.commit()
    await db.refresh(plan)
    return plan


@router.delete("/{plan_id}", status_code=204)
async def delete_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        await delete_workout_plan(db, current_user.id, plan_id)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(500, detail=str(e)) from e

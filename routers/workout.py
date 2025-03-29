# routers/workout.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.workout import *
from controllers.workout import *
from services.db import get_db, get_current_user
from services.auth import get_current_user
from models.auth import User

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


# TODO: Add similar PUT and DELETE endpoints
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

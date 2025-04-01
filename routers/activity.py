from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from controllers.activity import get_activities, get_activity
from schemas.activity import ActivityResponse
from models.activity import Activity
from sqlalchemy.ext.asyncio import AsyncSession

from services.db import get_db

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("/", response_model=List[ActivityResponse])
async def get_activities_endpoint(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    keyword: Optional[str] = Query(
        None, description="Keyword to search in name and description"
    ),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    sort: Optional[str] = Query(
        None, description="Sort by column (e.g., 'name' or '-name' for descending)"
    ),
    filter: Optional[str] = Query(
        None,
        description="Filter by column and value (e.g., 'target_muscle_group:Glutes')",
    ),
    db: AsyncSession = Depends(get_db),
):
    filters = {}
    if filter:
        try:
            key, value = filter.split(":")
            if hasattr(Activity, key):
                filters[key] = value
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail="Invalid filter format. Use 'column_name:value'.",
            ) from e

    valid_sort_columns = [column.name for column in Activity.__table__.columns]
    if sort and sort.lstrip("-") not in valid_sort_columns:
        sort = None

    # try:
    return await get_activities(
        db, page=page, limit=limit, keyword=keyword, sort=sort, filters=filters
    )
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=500, detail=f"Error retrieving activities: {str(e)}"
    #     ) from e


@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity_endpoint(activity_id: str, db: AsyncSession = Depends(get_db)):
    activity = await get_activity(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity

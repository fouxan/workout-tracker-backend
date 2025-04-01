from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc, desc
from typing import Optional
from models.activity import Activity


async def get_activities(
    db: AsyncSession,
    page: int = 1,
    limit: int = 10,
    keyword: Optional[str] = None,
    sort: Optional[str] = None,
    filters: Optional[dict] = None,
):
    query = select(Activity)

    if keyword:
        query = query.where(Activity.name.ilike(f"%{keyword}%"))

    # Apply filters
    if filters:
        for field, value in filters.items():
            if hasattr(Activity, field):
                query = query.where(getattr(Activity, field) == value)

    # Apply sorting
    if sort:
        sort_field = sort.lstrip("-")
        if hasattr(Activity, sort_field):
            sort_method = desc if sort.startswith("-") else asc
            query = query.order_by(sort_method(getattr(Activity, sort_field)))

    # Apply pagination
    offset = (page - 1) * limit
    result = await db.execute(query.offset(offset).limit(limit))
    return result.scalars().all()


async def get_activity(db: AsyncSession, activity_id: str):
    result = await db.execute(select(Activity).where(Activity.id == activity_id))
    return result.scalar_one_or_none()

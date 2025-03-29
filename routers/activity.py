from fastapi import APIRouter, HTTPException, Query
import sqlite3
from typing import Optional, List
import json
from models.activity import Activity

DATABASE_NAME = "fitness.db"

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("/", response_model=List[Activity])
async def get_activity(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    keyword: Optional[str] = Query(None, description="Keyword to search in name and description"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    sort: Optional[str] = Query(None, description="Sort by column (e.g., 'name' or '-name' for descending)"),
    filter: Optional[str] = Query(None, description="Filter by column and value (e.g., 'target_muscle_group:Glutes')")
,):
    try:
        # Connect to the database
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Base query
        query = "SELECT * FROM activities"
        params = []

        # Apply filtering
        if filter:
            filter_parts = filter.split(":")
            if len(filter_parts) == 2:
                column, value = filter_parts
                query += f" WHERE {column} = ?"
                params.append(value)

        # Apply sorting
        if sort:
            if sort.startswith("-"):
                sort_column = sort[1:]
                sort_order = "DESC"
            else:
                sort_column = sort
                sort_order = "ASC"
            query += f" ORDER BY {sort_column} {sort_order}"
        
        # Apply keyword search
        if keyword:
            query += " WHERE name LIKE ?"
            params.extend([f"%{keyword}%"])

        # Apply pagination
        offset = (page - 1) * limit
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        # Execute the query
        cursor.execute(query, params)
        activities = cursor.fetchall()

        # Close the connection
        conn.close()

        activities_response  = []
        for activity in activities:
            activity_dict = {
                "id": activity[0],
                "name": activity[1],
                "target_muscle_group": activity[2],
                "activity_type": activity[3],
                "mechanics": activity[4],
                "force_type": activity[5],
                "experience_level": activity[6],
                "secondary_muscles": activity[7],
                "equipment": activity[8],
                "overview": activity[9],
                "instructions": activity[10],
                "tips": activity[11],
                "image_url": activity[12],
                "video_url": activity[13],
                "muscle_group_image_url":activity[14] ,
                "calories_125lbs": activity[15],
                "calories_155lbs": activity[16],
                "calories_185lbs": activity[17],
                "data_links": json.loads(activity[18]),
            }
            activities_response.append(Activity(**activity_dict))


        return activities_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{activity_id}", response_model=Activity)
async def get_activity_by_id(activity_id: int):
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Base query
        query = "SELECT * FROM activities WHERE id = ?"
        cursor.execute(query, [activity_id])
        activity = cursor.fetchone()

        # Close the connection
        conn.close()

        return activity

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# @router.post("/", response_model=Activity)
# async def create_activity(activity: Activity):
#     try:
#         return create_activity(activity)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
# @router.put("/{activity_id}", response_model=Activity)
# async def update_activity(activity_id: int, activity: Activity):
#     try:
#         return update_activity(activity_id, activity)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    

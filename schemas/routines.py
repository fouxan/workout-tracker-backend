from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

from models.activity import Activity

class RoutineCreate(BaseModel):
    name: str
    notes: Optional[str] = None
    description: Optional[str] = None
    exercises: List[Activity]

class RoutineResponse(RoutineCreate):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
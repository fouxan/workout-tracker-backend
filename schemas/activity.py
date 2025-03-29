from pydantic import BaseModel
from typing import List, Dict, Optional


class Activity(BaseModel):
    name: str
    force: str
    level: str
    mechanic: str
    equipment: str
    primary_muscles: List[str]
    secondary_muscles: List[str]
    instructions: List[str]
    category: str
    images: List[str]


class ActivityCreate(Activity):
    pass


class ActivityResponse(Activity):
    id: int

    class Config:
        orm_mode = True

# schemas/workout.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class SetCreate(BaseModel):
    set_number: int
    set_type: str = Field(..., regex="^(normal|drop|super)$")
    parameters: dict


class ExerciseCreate(BaseModel):
    activity_id: int
    order: int
    rest_between_sets: Optional[str]  # ISO 8601 duration format
    notes: Optional[str]
    sets: List[SetCreate]


class WorkoutTemplateCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    exercises: List[ExerciseCreate]


class SetResponse(BaseModel):
    set_number: int
    set_type: str
    parameters: dict

    class Config:
        orm_mode = True


class ExerciseResponse(BaseModel):
    activity_id: int
    order: int
    rest_between_sets: Optional[str]
    notes: Optional[str]
    sets: List[SetResponse]

    class Config:
        orm_mode = True


class WorkoutTemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    exercises: List[ExerciseResponse]

    class Config:
        orm_mode = True

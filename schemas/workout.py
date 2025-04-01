# schemas/workout.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class SetCreate(BaseModel):
    set_number: int
    set_type: str = Field(..., pattern="^(normal|drop|super)$")
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
        from_attributes = True


class ExerciseResponse(BaseModel):
    activity_id: int
    order: int
    rest_between_sets: Optional[str]
    notes: Optional[str]
    sets: List[SetResponse]

    class Config:
        from_attributes = True


class WorkoutTemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    exercises: List[ExerciseResponse]

    class Config:
        from_attributes = True


class SetStart(BaseModel):
    weight: float
    reps: int
    is_warmup: bool = False


class SetComplete(BaseModel):
    rpe: Optional[float] = Field(None, ge=6, le=10)
    notes: Optional[str] = None


class ExerciseStart(BaseModel):
    activity_id: int


class WorkoutStart(BaseModel):
    template_id: Optional[int] = None


class WorkoutResponse(BaseModel):
    id: int
    status: str
    start_time: datetime
    duration: Optional[float]
    exercises: List[dict]

    class Config:
        from_attributes = True


class RealTimeUpdate(BaseModel):
    type: str  # 'set_start', 'set_complete', 'exercise_start', 'pause'
    data: dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# schemas/plan.py
from pydantic import BaseModel, Field, validator
from datetime import date
from typing import List, Optional


class ScheduledWorkoutCreate(BaseModel):
    template_id: int
    scheduled_time: Optional[str] = Field(
        None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"
    )
    is_completed: Optional[bool] = False


class PlanDayCreate(BaseModel):
    day_number: int = Field(..., gt=0)
    focus_area: Optional[str] = None
    notes: Optional[str] = None
    workouts: List[ScheduledWorkoutCreate]


class WorkoutPlanCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    start_date: date
    end_date: date
    days: List[PlanDayCreate]

    @validator("end_date")
    def end_date_after_start(cls, v, values):
        if "start_date" in values and v < values["start_date"]:
            raise ValueError("End date must be after start date")
        return v


class ScheduledWorkoutResponse(ScheduledWorkoutCreate):
    id: int
    template_name: str

    class Config:
        from_attributes = True


class PlanDayResponse(PlanDayCreate):
    id: int
    workouts: List[ScheduledWorkoutResponse]


class WorkoutPlanResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: date
    end_date: date
    is_active: bool
    days: List[PlanDayResponse]

    class Config:
        from_attributes = True

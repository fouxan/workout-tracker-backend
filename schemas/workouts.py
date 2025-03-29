from ast import List
from pydantic import BaseModel

class Workout(BaseModel):
    user_id: str
    workout_id: str
    name: str
    description: str
    notes: str
    


class UserWorkout(BaseModel):
    user_id: str
    routine_id: str
    workout_name: str
    workout_description: str
    workout_notes: str
    workout_exercises: List[str]
    rest_periods: List[int]
    start_time: str
    end_time: str
    duration: str
    status: str
    calories_burned: int
    user_rating: int


class WorkoutExercise(BaseModel):
    exercise_id: str
    exercise_name: str
    exercise_description: str
    exercise_notes: str
    exercise_sets: int
    exercise_reps: int
    exercise_weight: int
    exercise_duration: int
    exercise_calories_burned: int
    exercise_rating: int
    exercise_notes: str
    exercise_status: str

class WorkoutStart(BaseModel):
    user_id: str
    routine_id: str
    workout_name: str
    workout_description: str
    workout_notes: str
    workout_exercises: List[WorkoutExercise]
    rest_periods: List[int]
    start_time: str
    end_time: str
    duration: str
    status: str
    calories_burned: int
    user_rating: int
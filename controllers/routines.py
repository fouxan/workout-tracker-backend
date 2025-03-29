# controllers/routines.py
from fastapi import Depends, HTTPException
from models.routines import RoutineCreate, RoutineUpdate, RoutineInDB
from models.workouts import Workout
from models.activity import Activity
from typing import Optional, List
import logging
import os
from google import genai
import sqlite3

from services.db import DATABASE_NAME

logger = logging.getLogger(__name__)

# Initialize Gemini client
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
client = genai.GenerativeModel('gemini-2.0-flash')

async def analyze_routine_with_ai(routine: RoutineInDB, exercises: List[Activity]) -> str:
    """Helper function to analyze routine using Gemini"""
    try:
        prompt = f"""
        Analyze this fitness routine and provide structured feedback:
        Routine Name: {routine.name}
        Description: {routine.description}
        Notes: {routine.notes}
        Exercises: {[e.name for e in exercises]}
        
        Consider factors like:
        - Muscle group balance
        - Exercise variety
        - Potential overtraining risks
        - Recommended modifications
        - Equipment requirements
        - Skill progression
        
        Provide response in JSON format with keys:
        summary, strengths, areas_for_improvement, recommendations
        """
        
        response = client.generate_content(
            contents=prompt,
            generation_config={
                "response_mime_type": "application/json",
            }
        )
        return response.text
    except Exception as e:
        logger.error(f"AI Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail="AI analysis failed")

# controllers/workouts.py
from fastapi import HTTPException
from models.workouts import WorkoutStart, WorkoutUpdate, WorkoutInDB, WorkoutExerciseUpdate
from typing import Optional, List
import logging
from datetime import datetime
from google import genai
from controllers.routines import get_routine

logger = logging.getLogger(__name__)
client = genai.Client(api_key='AIzaSyAKPBbfsR0mgEGUBfOslnnEMn9l1xaAU4A')

async def start_workout(
    workout_data: WorkoutStart, 
    user_id: str
) -> WorkoutInDB:
    """Start a new workout session"""
    try:
        # If using a routine, validate ownership
        if workout_data.routine_id:
            routine = await get_routine(workout_data.routine_id, user_id)
            
        # Create initial workout object
        new_workout = WorkoutInDB(
            **workout_data.dict(exclude={"routine_id"}),
            user_id=user_id,
            start_time=datetime.now(),
            end_time=None,
            status="active",
            ai_analysis=None
        )
        # await db.execute(insert(Workout).values(new_workout.dict()))
        return new_workout
    except Exception as e:
        logger.error(f"Workout start failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Workout start failed")

async def update_workout_stats(
    workout_id: str,
    updates: WorkoutUpdate,
    user_id: str
) -> WorkoutInDB:
    """Update workout statistics during session"""
    workout = await get_workout(workout_id, user_id)
    
    # Validate workout is still active
    if workout.status != "active":
        raise HTTPException(status_code=400, detail="Cannot update completed workout")
    
    # Apply updates
    updated = workout.copy(update=updates.dict(exclude_unset=True))
    # await db.execute(update(...))
    return updated

async def end_workout(workout_id: str, user_id: str) -> WorkoutInDB:
    """Finalize a workout session"""
    workout = await get_workout(workout_id, user_id)
    
    # Calculate duration
    end_time = datetime.now()
    duration = end_time - workout.start_time
    
    updates = {
        "end_time": end_time,
        "status": "completed",
        "duration": duration.total_seconds()
    }
    
    # await db.execute(update(...))
    return await update_workout_stats(workout_id, WorkoutUpdate(**updates), user_id)

async def analyze_workout_with_ai(workout: WorkoutInDB) -> str:
    """Generate AI analysis for completed workout"""
    try:
        prompt = f"""
        Analyze this workout session and provide structured feedback:
        Duration: {workout.duration} seconds
        Exercises: {[e.name for e in workout.exercises]}
        Stats: {workout.stats}
        
        Consider:
        - Intensity analysis
        - Volume adequacy
        - Rest period effectiveness
        - Form suggestions
        - Progress tracking
        - Recovery recommendations
        
        Provide response in JSON format with keys:
        summary, intensity_analysis, volume_analysis, recovery_advice
        """
        
        response = client.generate_content(
            contents=prompt,
            generation_config={
                "response_mime_type": "application/json",
            }
        )
        return response.text
    except Exception as e:
        logger.error(f"Workout analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Workout analysis failed")

def get_all_workouts(user_id: str) -> List[WorkoutInDB]:
    """Get all workouts for a user"""
    # workouts = await db.fetch_all(select(...))
    pass

async def get_workout(workout_id: str, user_id: str) -> WorkoutInDB:
    """Get a single workout by ID"""
    # workout = await db.fetch_one(select(...))
    if not workout or workout.user_id != user_id:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout

async def update_workout_exercises(
    workout_id: str, 
    updates: List[WorkoutExerciseUpdate], 
    user_id: str
) -> WorkoutInDB:
    """Update exercises within a workout"""
    workout = await get_workout(workout_id, user_id)
    
    # Validate workout is still active
    if workout.status != "active":
        raise HTTPException(status_code=400, detail="Cannot update completed workout")
    
    # Apply updates
    updated_exercises = []
    for update in updates:
        exercise = next((e for e in workout.exercises if e.id == update.exercise_id), None)
        if exercise:
            updated_exercise = exercise.copy(update=update.dict(exclude_unset=True))
            updated_exercises.append(updated_exercise)
    
    # await db.execute(update(...))
    return workout.copy(update={"exercises": updated_exercises})




def create_workout(
        workout_data: Workout,
        user_id: str,
        analyze: bool = False
):
    """Create a new workout with optional AI analysis"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        # Create basic workout (replace with actual DB call)
        new_workout = Workout(
            **workout_data.dict(),
            user_id=user_id,
            ai_analysis=None
        )
        # await db.execute(insert(Workout).values(new_workout.dict()))
        
        if analyze:
            # Get exercise details (replace with actual DB call)
            exercises = []  # await get_exercises_by_ids([e.id for e in workout_data.activities])
            analysis = await analyze_routine_with_ai(new_workout, exercises)
            new_workout.ai_analysis = analysis
            # Update workout with analysis
            # await db.execute(update(Workout).where(...))
        
        return new_workout
    except Exception as e:
        logger.error(f"Workout creation failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Workout creation failed")
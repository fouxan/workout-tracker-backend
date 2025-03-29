from fastapi import APIRouter, Depends, HTTPException
from models.routines import RoutineCreate, RoutineResponse
import sqlite3
from middleware.auth import get_current_user
from typing import Optional, List
import json

DATABASE_NAME = "fitness.db"

router = APIRouter(prefix="/routines", tags=["routines"])

# Create routine with exercises
@router.post("/", response_model=RoutineResponse)
async def create_routine(routine: RoutineCreate, user=Depends(get_current_user)):
    try:
        # Create routine
        routine_data = {
            "user_id": user['id'],
            "name": routine.name,
            "description": routine.description
        }
        res = supabase.table("routines").insert(routine_data).execute()
        print("Routine created", res)
        new_routine = res.data[0]
      
        # Add exercises
        exercises = [{
            "routine_id": new_routine["id"],
            "exercise_id": ex.exercise_id,
            "sets": ex.sets,
            "reps": ex.reps,
            "sequence_order": ex.sequence_order,
            "rest_seconds": ex.rest_seconds
        } for ex in routine.exercises]
      
        supabase.table("routine_exercises").insert(exercises).execute()
      
        return {**new_routine, "exercises": exercises}
  
    except Exception as e:
        raise HTTPException(400, detail=str(e))
    

# Get routine details with exercises
@router.get("/{routine_id}", response_model=RoutineResponse)
async def get_routine(routine_id: str, user=Depends(get_current_user)):
    try:
        # Verify ownership
        routine = supabase.table("routines")\
                        .select("*")\
                        .eq("id", routine_id)\
                        .eq("user_id", user.id)\
                        .single()\
                        .execute().data
      
        # Get exercises
        exercises = supabase.table("routine_exercises")\
                          .select("exercise_id, sets, reps, sequence_order, rest_seconds")\
                          .eq("routine_id", routine_id)\
                          .order("sequence_order")\
                          .execute().data
      
        return {**routine, "exercises": exercises}
  
    except Exception as e:
        raise HTTPException(404, detail="Routine not found")


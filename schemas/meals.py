from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date
from enum import Enum as PyEnum
from pydantic import BaseModel
from typing import List, Optional

Base = declarative_base()

class MealType(str, PyEnum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    OTHER = "other"

class Food(Base):
    __tablename__ = "foods"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    quantity = Column(Float, nullable=True, default=100)
    quantity_unit = Column(String, nullable=True, default="grams")
    food_type = Column(String, nullable=True, default="generic")
    food_url = Column(String, nullable=True)
    calories = Column(Integer, nullable=False)
    protein = Column(Float, nullable=True)
    carbs = Column(Float, nullable=True)
    fats = Column(Float, nullable=True)

class Meal(Base):
    __tablename__ = "meals"
    id = Column(Integer, primary_key=True, index=True)
    meal_type = Column(Enum(MealType), nullable=False)
    timestamp = Column(DateTime, nullable=True)
    notes = Column(String, nullable=True)
    day_id = Column(Integer, ForeignKey("days.id"))
    foods = relationship("Food", secondary="meal_foods")

class MealFood(Base):
    __tablename__ = "meal_foods"
    meal_id = Column(Integer, ForeignKey("meals.id"), primary_key=True)
    food_id = Column(Integer, ForeignKey("foods.id"), primary_key=True)

class Day(Base):
    __tablename__ = "days"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    total_calories_consumed = Column(Float, nullable=True)
    total_calories_burned = Column(Float, nullable=True)
    total_protein = Column(Float, nullable=True)
    total_carbs = Column(Float, nullable=True)
    total_fats = Column(Float, nullable=True)
    meals = relationship("Meal", backref="day")
    workouts = relationship("Workout", backref="day")
    muscle_group_activation = Column(String, nullable=True)
    activity_level = Column(String, nullable=True)
    overall_score = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)

class MealPlan(Base):
    __tablename__ = "meal_plans"
    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    days = relationship("Day", backref="meal_plan")


# Pydantic schemas for request/response
class FoodCreate(BaseModel):
    name: str
    description: Optional[str] = None
    quantity: Optional[float] = 100
    quantity_unit: Optional[str] = "grams"
    food_type: Optional[str] = "generic"
    food_url: Optional[str] = None
    calories: int
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fats: Optional[float] = None

class MealCreate(BaseModel):
    meal_type: MealType
    foods: List[int]  # List of food IDs
    timestamp: Optional[datetime] = None
    notes: Optional[str] = None

class DayCreate(BaseModel):
    date: date
    meals: List[int]  # List of meal IDs

class MealPlanCreate(BaseModel):
    start_date: date
    end_date: date
    days: List[int]  # List of day IDs
    notes: Optional[str] = None

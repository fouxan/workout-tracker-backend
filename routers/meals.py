from typing import List
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
import controllers.meals as meals
from models.meals import Day, DayCreate, FoodCreate, Meal, MealCreate, MealPlan, MealPlanCreate, Food
from services.db import get_db_connection

router = APIRouter(prefix="/meals", tags=["meals"])
security = HTTPBearer()


@router.post("/log-meal/")
def log_meal(meal_id: int):
    return meals.log_meal(meal_id=meal_id)

@router.post("/mark-meal-complete/")
def mark_meal_complete(meal_id: int, meal_plan_id: int):
    return meals.mark_meal_complete(meal_id=meal_id, meal_plan_id=meal_plan_id)

@router.get("/meal-plans/{meal_plan_id}/")
def get_meal_plan(meal_plan_id: int):
    return meals.get_meal_plan(meal_plan_id=meal_plan_id)

@router.get("/meal-plans/", response_model=List[MealPlan])
def get_meal_plans():
    return meals.get_meal_plans()

@router.post("/meal-plans/", response_model=MealPlan)
def create_meal_plan(meal_plan: MealPlanCreate):
    return meals.create_meal_plan(meal_plan=meal_plan,)

@router.put("/meal-plans/{meal_plan_id}", response_model=MealPlan)
def update_meal_plan(meal_plan_id: int, meal_plan: MealPlanCreate):
    return meals.update_meal_plan(meal_plan_id=meal_plan_id, meal_plan=meal_plan)


@router.get("/days/", response_model=List[Day])
def get_days():
    return meals.get_days()

@router.post("/days/", response_model=Day)
def create_day(day: DayCreate):
    return meals.create_day(day=day)

@router.put("/days/{day_id}", response_model=Day)
def update_day(day_id: int, day: DayCreate):
    return meals.update_day(day_id=day_id, day=day)


@router.get("/meals/{meal_id}/", response_model=Meal)
def get_meal(meal_id: int):
    return meals.get_meal(meal_id=meal_id)

# Paginate this endpoint
@router.get("/meals/", response_model=List[Meal])
def get_meals():
    return meals.get_meals()

@router.post("/meals/", response_model=Meal)
def create_meal(meal: MealCreate):
    return meals.create_meal(meal=meal)

@router.put("/meals/{meal_id}", response_model=Meal)
def update_meal(meal_id: int, meal: MealCreate):
    return meals.update_meal(meal_id=meal_id, meal=meal)

@router.get("/foods/", response_model=List[Food])
def get_foods():
    return meals.get_foods()

@router.post("/foods/", response_model=Food)
def create_food(food: FoodCreate):
    return meals.create_food(food=food)

@router.put("/foods/{food_id}", response_model=Food)
def update_food(food_id: int, food: FoodCreate):
    return meals.update_food(food_id=food_id, food=food)

@router.get("/search-foods/")
def search_foods(query: str):
    # Call your existing function to search foods
    foods = meals.search_food(query)  # Replace with your function
    return foods

@router.get("/search-recipes/")
def search_recipes(query: str):
    # Call your existing function to search recipes
    recipes = meals.search_recipe(query)  # Replace with your function
    return recipes

import requests
from services.db import get_db_connection
from sqlalchemy.orm import Session
from models.meals import FoodCreate, MealCreate, DayCreate, MealPlanCreate, Food, MealPlan, Meal, Day
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from models.meals import (
    FoodCreate, MealCreate, DayCreate, MealPlanCreate,
    Food, Meal, Day, MealPlan
)
from services.db import get_db_connection
from middleware.auth import get_current_user

FATSECRET_BASE_URL = "https://platform.fatsecret.com/rest/"
FATSECRET_URLS = {
  "token":
    "https://oauth.fatsecret.com/connect/token",
  "food_search":
    f"{FATSECRET_BASE_URL}/foods/search/v1",
  "food_search_by_id":
    f"{FATSECRET_BASE_URL}/food/v4",
  "recipe_search":
    f"{FATSECRET_BASE_URL}/recipes/search/v3",
  "recipe_search_by_id":
    f"{FATSECRET_BASE_URL}/recipe/v2",
}
FATSECRET_CLIENT_ID = "YOUR_CLIENT"
FATSECRET_CLIENT_SECRET = ""


def generate_fatsecret_token(client_id, client_secret):
  try:
    response = requests.post(
      url="https://oauth.fatsecret.com/connect/token",
      data={
          "grant_type": "client_credentials",
          "scope": "basic",
      },
      auth=(client_id, client_secret)
    )

    if not response.status_code == 200:
      return {
        "error": response.text
      }

    data = response.json()
    access_token = data.get("access_token")
    if not access_token:
      return {
        "error": data
      }

    return access_token
  except Exception as e:
    return {"error": str(e)}

def search_food(food_name, token, region = 'EN', language = 'en', max_results = 20, page_number = None):
  try:
    headers = {
      "Authorization": f"Bearer {token}",
      "Content-Type": "application/json"
    }
    response = requests.get(
      url=FATSECRET_URLS["food_search"],
      headers=headers,
      params={
          "method": "foods.search",
          "search_expression": food_name,
          "region": region,
          "language": language,
          "max_results": max_results,
          "page_number": page_number,
          "format": "json",
      }
    )

    if not response.status_code == 200:
      return {
        "error": response.text
      }

    data = response.json()
    foods = data.get("foods")
    if not foods or not foods.get("food"):
      return {
        "error": data
      }

    food =  foods.get("food")
    quantity = food.get("food_description").split("-")[0].strip()
    nutrition = food.get("food_description").split("-")[1].strip()

    calories = nutrition.split("|")[0].split(":")[1].strip()
    fat = nutrition.split("|")[1].split(":")[1].strip()
    carbohydrate = nutrition.split("|")[2].split(":")[1].strip()
    protein = nutrition.split("|")[3].split(":")[1].strip()

    return {
      "id": food.get("food_id"),
      "name": food.get("food_name"),
      "description": food.get("food_description"),
      "brand": food.get("brand_name"),
      "type": food.get("serving_size"),
      "url": food.get("url"),
      "quantity": quantity,
      "calories": calories,
      "fat": fat,
      "carbohydrate": carbohydrate,
      "protein": protein,
    }
  
  except Exception as e:
    return {"error": str(e)}

def search_recipe(recipe_name, token):
  response = requests.get(
    url="https://platform.fatsecret.com/rest/server.api",
    params={
        "method": "recipes.search",
        "search_expression": recipe_name,
        "format": "json",
        "oauth_consumer_key": token["client_id"],
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": token["timestamp"],
        "oauth_nonce": token["nonce"],
        "oauth_version": "1.0",
        "oauth_signature": token["signature"]
    }
  )

  return response.json()


# Endpoints
def create_food(food: FoodCreate, db: Session = Depends(get_db_connection)):
    db_food = Food(**food.dict())
    db.add(db_food)
    db.commit()
    db.refresh(db_food)
    return db_food

def create_meal(meal: MealCreate, db: Session = Depends(get_db_connection)):
    db_meal = Meal(meal_type=meal.meal_type, timestamp=meal.timestamp, notes=meal.notes)
    for food_id in meal.foods:
        food = db.query(Food).filter(Food.id == food_id).first()
        if not food:
            raise HTTPException(status_code=404, detail=f"Food with ID {food_id} not found")
        db_meal.foods.append(food)
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal

def create_day(day: DayCreate, db: Session = Depends(get_db_connection)):
    db_day = Day(date=day.date)
    for meal_id in day.meals:
        meal = db.query(Meal).filter(Meal.id == meal_id).first()
        if not meal:
            raise HTTPException(status_code=404, detail=f"Meal with ID {meal_id} not found")
        db_day.meals.append(meal)
    db.add(db_day)
    db.commit()
    db.refresh(db_day)
    return db_day

def create_meal_plan(meal_plan: MealPlanCreate, db: Session = Depends(get_db_connection)):
    db_meal_plan = MealPlan(start_date=meal_plan.start_date, end_date=meal_plan.end_date, notes=meal_plan.notes)
    for day_id in meal_plan.days:
        day = db.query(Day).filter(Day.id == day_id).first()
        if not day:
            raise HTTPException(status_code=404, detail=f"Day with ID {day_id} not found")
        db_meal_plan.days.append(day)
    db.add(db_meal_plan)
    db.commit()
    db.refresh(db_meal_plan)
    return db_meal_plan

def log_meal(meal_id: int, db: Session = Depends(get_db_connection)):
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    day = meal.day
    if not day:
        raise HTTPException(status_code=404, detail="Day not found for this meal")
    # Update daily calories
    day.total_calories = (day.total_calories or 0) + sum(food.calories for food in meal.foods)
    db.commit()
    return {"message": "Meal logged and daily calories updated"}

def get_meal(meal_id: int, db: Session = Depends(get_db_connection)):
    meal = db.query(Meal).filter(Meal.id == meal_id).first()
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    return meal

def get_meal_plan(db: Session, meal_plan_id: int):
    meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
    if not meal_plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return meal_plan

def get_day(db: Session, day_id: int):
    day = db.query(Day).filter(Day.id == day_id).first()
    if not day:
        raise HTTPException(status_code=404, detail="Day not found")
    return day

def get_food(db: Session, food_id: int):
    food = db.query(Food).filter(Food.id == food_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")
    return food

# Protected endpoints
def log_meal(meal_id: int, db: Session = Depends(get_db_connection), user_id: int = Depends(get_current_user)):
    meal = get_meal(db, meal_id)
    day = meal.day
    if not day:
        raise HTTPException(status_code=404, detail="Day not found for this meal")
    # Update daily calories
    day.total_calories = (day.total_calories or 0) + sum(food.calories for food in meal.foods)
    db.commit()
    return {"message": "Meal logged and daily calories updated"}

def mark_meal_complete(meal_id: int, meal_plan_id: int, db: Session = Depends(get_db_connection), user_id: int = Depends(get_current_user)):
    meal = get_meal(db, meal_id)
    
    meal_plan = get_meal_plan(db, meal_plan_id)
    # Mark meal as completed (add your logic here)
    return {"message": "Meal marked as completed"}

def get_meal_plan(meal_plan_id: int, db: Session = Depends(get_db_connection), user_id: int = Depends(get_current_user)):
    meal_plan = get_meal_plan(db, meal_plan_id)
    return meal_plan

def get_meal_plans(db: Session = Depends(get_db_connection), user_id: int = Depends(get_current_user)):
    return db.query(MealPlan).all()

def create_meal_plan(meal_plan: MealPlanCreate, db: Session = Depends(get_db_connection), user_id: int = Depends(get_current_user)):
    db_meal_plan = MealPlan(**meal_plan.dict())
    db.add(db_meal_plan)
    db.commit()
    db.refresh(db_meal_plan)
    return db_meal_plan

def update_meal_plan(meal_plan_id: int, meal_plan: MealPlanCreate, db: Session = Depends(get_db_connection), user_id: int = Depends(get_current_user)):
    db_meal_plan = get_meal_plan(db, meal_plan_id)
    for key, value in meal_plan.dict().items():
        setattr(db_meal_plan, key, value)
    db.commit()
    db.refresh(db_meal_plan)
    return db_meal_plan

def get_days(db: Session = Depends(get_db_connection), user_id: int = Depends(get_current_user)):
    return db.query(Day).all()

def create_day(day: DayCreate, db: Session = Depends(get_db_connection), user_id: int = Depends(get_current_user)):
    db_day = Day(**day.dict())
    db.add(db_day)
    db.commit()
    db.refresh(db_day)
    return db_day

def update_day(day_id: int, day: DayCreate, db: Session = Depends(get_db_connection), user_id: int = Depends(get_current_user)):
    db_day = get_day(db, day_id)
    for key, value in day.dict().items():
        setattr(db_day, key, value)
    db.commit()
    db.refresh(db_day)
    return db_day

def get_meal(meal_id: int, db: Session = Depends(get_db_connection), user_id: int = Depends(get_current_user)):
    return get_meal(db, meal_id)

def get_meals(db: Session = Depends(get_db_connection), user_id: int = Depends(get_current_user)):
    return db.query(Meal).all()

def create_meal(meal: MealCreate, db: Session = Depends(get_db_connection), user_id: int = Depends(get_current_user)):
    db_meal = Meal(**meal.dict())
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)
    return db_meal

def update_meal(meal_id: int, meal: MealCreate, db: Session = Depends(get_db_connection), user_id: int = Depends(get_current_user)):
    db_meal = get_meal(db, meal_id)
    for key, value in meal.dict().items():
        setattr(db_meal, key, value)
    db.commit()
    db.refresh(db_meal)
    return db_meal

def get_foods(db: Session = Depends(get_db_connection), user_id: int = Depends(get_current_user)):
    return db.query(Food).all()

def create_food(food: FoodCreate, db: Session = Depends(get_db_connection), user_id: int = Depends(get_current_user)):
    db_food = Food(**food.dict())
    db.add(db_food)
    db.commit()
    db.refresh(db_food)
    return db_food

def update_food(food_id: int, food: FoodCreate, db: Session = Depends(get_db_connection), user_id: int = Depends(get_current_user)):
    db_food = get_food(db, food_id)
    for key, value in food.dict().items():
        setattr(db_food, key, value)
    db.commit()
    db.refresh(db_food)
    return db_food

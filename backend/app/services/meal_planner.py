"""
Meal Planner: Assembles a personalized 7-day nutritional meal plan.
"""

from datetime import date
from typing import Any, Dict, List
import random
from sqlalchemy.orm import Session

from ..models.analysis import MealPlan
from ..models.nutrition import Food
from ..models.user import HealthProfile

MEAL_SLOTS = ["breakfast", "lunch", "dinner", "snack"]


def generate_7day_meal_plan(user_id: int, prediction_id: int, db: Session) -> Dict[str, Any]:
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == user_id).first()
    restrictions = [r.lower() for r in (profile.dietary_restrictions if profile else [])]

    query = db.query(Food)
    if "vegetarian" in restrictions:
        query = query.filter(Food.is_vegetarian == True)
    if "vegan" in restrictions:
        query = query.filter(Food.is_vegan == True)
    if "gluten_free" in restrictions:
        query = query.filter(Food.is_gluten_free == True)
    if "dairy_free" in restrictions:
        query = query.filter(Food.is_dairy_free == True)

    available_foods = query.all()
    if not available_foods:
        available_foods = db.query(Food).all()

    plan_days: List[Dict[str, Any]] = []

    for day_num in range(1, 8):
        day_meals = {}
        daily_calories = 0.0

        for slot in MEAL_SLOTS:
            matching = [f for f in available_foods if slot in (f.suitable_meals or [])]
            selected = random.choice(matching) if matching else random.choice(available_foods)

            day_meals[slot] = {
                "food_id": selected.id,
                "name": selected.name,
                "serving": selected.serving_description,
                "calories": selected.calories,
                "protein_g": selected.protein_g,
                "iron_mg": selected.iron_mg,
                "calcium_mg": selected.calcium_mg,
            }
            daily_calories += selected.calories

        plan_days.append({
            "day": day_num,
            "meals": day_meals,
            "daily_calories": round(daily_calories, 1),
        })

    db.query(MealPlan).filter(MealPlan.user_id == user_id).delete()

    record = MealPlan(
        user_id=user_id,
        start_date=date.today(),
        generated_from_prediction_id=prediction_id,
        plan=plan_days,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "start_date": record.start_date,
        "plan": plan_days,
    }
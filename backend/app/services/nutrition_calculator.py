from typing import List
from ..models.nutrition import FoodDiaryEntry


def calculate_daily_nutrition(entries: List[FoodDiaryEntry]) -> dict:
    """Computes total macronutrients and tracked micronutrients from diary entries."""
    totals = {
        "calories": 0.0,
        "protein_g": 0.0,
        "carbs_g": 0.0,
        "fat_g": 0.0,
        "fiber_g": 0.0,
        "iron_mg": 0.0,
        "calcium_mg": 0.0,
        "vitamin_d_mcg": 0.0,
        "vitamin_b12_mcg": 0.0,
        "vitamin_c_mg": 0.0,
    }

    for entry in entries:
        food = entry.food
        if not food:
            continue
        qty = entry.quantity
        totals["calories"] += food.calories * qty
        totals["protein_g"] += food.protein_g * qty
        totals["carbs_g"] += food.carbs_g * qty
        totals["fat_g"] += food.fat_g * qty
        totals["fiber_g"] += food.fiber_g * qty
        totals["iron_mg"] += food.iron_mg * qty
        totals["calcium_mg"] += food.calcium_mg * qty
        totals["vitamin_d_mcg"] += food.vitamin_d_mcg * qty
        totals["vitamin_b12_mcg"] += food.vitamin_b12_mcg * qty
        totals["vitamin_c_mg"] += food.vitamin_c_mg * qty

    return {k: round(v, 2) for k, v in totals.items()}
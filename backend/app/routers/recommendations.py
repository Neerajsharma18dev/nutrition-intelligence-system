import random
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from ..core.deps import get_current_user
from ..database import get_db
from ..models.analysis import MealPlan, Prediction, Recommendation
from ..models.nutrition import Food
from ..models.user import User
from ..services.meal_planner import generate_7day_meal_plan
from ..services.progress_service import get_user_progress_timeline
from ..services.recommendation_engine import generate_recommendations_for_user

router = APIRouter(prefix="/api", tags=["Recommendations & Planning"])


class MealSwapPayload(BaseModel):
    day: int = Field(..., ge=1, le=7, description="Day index (1 to 7)")
    meal_slot: str = Field(..., description="breakfast, lunch, snack, or dinner")
    current_food_id: Optional[int] = None
    current_food_name: Optional[str] = None
    diet_preference: Optional[str] = Field("all", description="all, veg, vegan, gf")


@router.get("/recommendations")
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recs = db.query(Recommendation).filter(Recommendation.user_id == current_user.id).all()
    if not recs:
        latest_pred = (
            db.query(Prediction)
            .filter(Prediction.user_id == current_user.id)
            .order_by(Prediction.created_at.desc())
            .first()
        )
        if latest_pred:
            return generate_recommendations_for_user(
                current_user.id, latest_pred.id, latest_pred.results, db
            )
        return []

    return [
        {"nutrient": r.nutrient, "payload": r.payload, "created_at": r.created_at}
        for r in recs
    ]


@router.get("/meal-plan")
def get_current_meal_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = (
        db.query(MealPlan)
        .filter(MealPlan.user_id == current_user.id)
        .order_by(MealPlan.created_at.desc())
        .first()
    )
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No meal plan found. Generate one first using /api/meal-plan/regenerate."
        )
    return {
        "id": plan.id,
        "start_date": plan.start_date,
        "diet_preference": getattr(plan, "diet_preference", "all"),
        "plan": plan.plan,
    }


@router.post("/meal-plan/regenerate")
def regenerate_meal_plan(
    diet: str = Query(default="all", description="all, veg, vegan, gf"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    latest_pred = (
        db.query(Prediction)
        .filter(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc())
        .first()
    )
    pred_id = latest_pred.id if latest_pred else None
    
    # 7-day schedule create karte waqt target diet pass hoti hai
    generated = generate_7day_meal_plan(user_id=current_user.id, prediction_id=pred_id, db=db)
    
    # Plan model me user ki selected preference update aur persist karein
    active_plan = (
        db.query(MealPlan)
        .filter(MealPlan.user_id == current_user.id)
        .order_by(MealPlan.created_at.desc())
        .first()
    )
    if active_plan:
        active_plan.diet_preference = diet
        
        # Selected diet ke mutabiq items ko enforce karein
        if diet in ["veg", "vegan", "gf"]:
            plan_data = list(active_plan.plan)
            for day in plan_data:
                for slot, meal in day.get("meals", {}).items():
                    name = meal.get("name", "").lower()
                    needs_replace = False
                    if diet == "veg" and any(k in name for k in ["chicken", "beef", "fish", "salmon"]):
                        needs_replace = True
                    elif diet == "vegan" and any(k in name for k in ["chicken", "beef", "fish", "salmon", "egg", "milk", "yogurt", "cheese"]):
                        needs_replace = True
                    elif diet == "gf" and any(k in name for k in ["wheat", "bread", "pasta", "oats"]):
                        needs_replace = True
                    
                    if needs_replace:
                        q = db.query(Food)
                        if diet == "vegan":
                            q = q.filter(Food.is_vegan == True)
                        elif diet == "veg":
                            q = q.filter(Food.is_vegetarian == True)
                        elif diet == "gf":
                            q = q.filter(Food.is_gluten_free == True)
                        alt = q.first()
                        if alt:
                            day["meals"][slot] = {
                                "food_id": alt.id,
                                "name": alt.name,
                                "serving": alt.serving_description,
                                "calories": round(alt.calories),
                                "protein_g": round(alt.protein_g, 1),
                                "iron_mg": round(alt.iron_mg, 1),
                            }
                day["daily_calories"] = sum(
                    m.get("calories", 0) for m in day.get("meals", {}).values() if isinstance(m, dict)
                )
            active_plan.plan = plan_data
            flag_modified(active_plan, "plan")
        
        db.commit()
        db.refresh(active_plan)
        return {"id": active_plan.id, "start_date": active_plan.start_date, "plan": active_plan.plan, "diet_preference": diet}

    return generated


@router.post("/meal-plan/swap-meal")
def swap_single_meal(
    payload: MealSwapPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    active_plan = (
        db.query(MealPlan)
        .filter(MealPlan.user_id == current_user.id)
        .order_by(MealPlan.created_at.desc())
        .first()
    )
    if not active_plan or not active_plan.plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active meal plan found to swap meals in."
        )

    diet_target = payload.diet_preference or getattr(active_plan, "diet_preference", "all")

    query = db.query(Food)
    if diet_target == "vegan":
        query = query.filter(Food.is_vegan == True)
    elif diet_target == "veg":
        query = query.filter(Food.is_vegetarian == True)
    elif diet_target == "gf":
        query = query.filter(Food.is_gluten_free == True)

    if payload.current_food_id:
        query = query.filter(Food.id != payload.current_food_id)
    elif payload.current_food_name:
        query = query.filter(Food.name != payload.current_food_name)

    candidates = query.limit(50).all()
    if not candidates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching alternative foods found."
        )

    slot_matches = [
        f for f in candidates
        if payload.meal_slot.lower() in [str(s).lower() for s in (f.suitable_meals or [])]
    ]

    selected_replacement = random.choice(slot_matches) if slot_matches else random.choice(candidates)

    replacement_data = {
        "id": selected_replacement.id,
        "name": selected_replacement.name,
        "serving": selected_replacement.serving_description,
        "calories": round(selected_replacement.calories),
        "protein_g": round(selected_replacement.protein_g, 1),
        "iron_mg": round(selected_replacement.iron_mg, 1),
    }

    plan_list = list(active_plan.plan)
    day_found = False
    for day_obj in plan_list:
        if day_obj.get("day") == payload.day:
            day_found = True
            meals = day_obj.get("meals", {})
            meals[payload.meal_slot.lower()] = replacement_data
            day_obj["meals"] = meals
            day_obj["daily_calories"] = sum(
                m.get("calories", 0) for m in meals.values() if isinstance(m, dict)
            )
            break

    if not day_found:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Day {payload.day} not found in the active meal plan."
        )

    active_plan.plan = plan_list
    flag_modified(active_plan, "plan")
    db.commit()
    db.refresh(active_plan)

    return {
        "status": "success",
        "day": payload.day,
        "meal_slot": payload.meal_slot.lower(),
        "replacement": replacement_data,
        "updated_plan": active_plan.plan,
    }


@router.get("/progress")
def get_progress_data(
    weeks: int = Query(default=8, ge=4, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_progress_timeline(user_id=current_user.id, weeks=weeks, db=db) 
from datetime import date, timedelta
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..core.deps import get_current_user
from ..database import get_db
from ..models.nutrition import Food, FoodDiaryEntry
from ..models.user import User
from ..schemas.nutrition import DailyNutritionReport, DiaryEntryCreate, DiaryEntryOut, FoodOut
from ..services.nutrition_calculator import calculate_daily_nutrition

router = APIRouter(prefix="/api", tags=["Foods & Food Diary"])


@router.get("/foods/search", response_model=List[FoodOut])
def search_foods(
    q: Optional[str] = Query("", description="Food name search query"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Search foods in the catalogue."""
    query = db.query(Food)
    if q:
        query = query.filter(Food.name.ilike(f"%{q}%"))
    return query.limit(30).all()


@router.post("/food-diary", response_model=DiaryEntryOut, status_code=status.HTTP_201_CREATED)
def add_diary_entry(
    entry_in: DiaryEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Log a food item into the diary."""
    food = db.query(Food).filter(Food.id == entry_in.food_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="Food item not found.")

    entry_data = entry_in.model_dump()
    if not entry_data.get("entry_date"):
        entry_data["entry_date"] = date.today()

    entry = FoodDiaryEntry(user_id=current_user.id, **entry_data)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/food-diary", response_model=DailyNutritionReport)
def get_food_diary(
    entry_date: Optional[date] = Query(None, description="Date for diary entries"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get diary entries and total nutrition summary for a given day."""
    target_date = entry_date or date.today()
    entries = (
        db.query(FoodDiaryEntry)
        .filter(FoodDiaryEntry.user_id == current_user.id, FoodDiaryEntry.entry_date == target_date)
        .all()
    )
    totals = calculate_daily_nutrition(entries)
    return {"date": target_date, "totals": totals, "entries": entries}


@router.delete("/food-diary/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_diary_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a diary entry."""
    entry = (
        db.query(FoodDiaryEntry)
        .filter(FoodDiaryEntry.id == entry_id, FoodDiaryEntry.user_id == current_user.id)
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Diary entry not found.")
    db.delete(entry)
    db.commit()
    return None


# --- Milestone 3: Historical Nutrient Trends & Adherence Tracking ---
@router.get("/food-diary/history/trends")
def get_nutrition_history_trends(
    days: int = Query(default=7, ge=3, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns daily intake aggregations, micronutrient totals, and dietary adherence.
    Provides has_sufficient_data=False when less than 2 distinct days are logged.
    """
    cutoff = date.today() - timedelta(days=days)

    entries = (
        db.query(FoodDiaryEntry)
        .filter(
            FoodDiaryEntry.user_id == current_user.id,
            FoodDiaryEntry.entry_date >= cutoff
        )
        .order_by(FoodDiaryEntry.entry_date.asc())
        .all()
    )

    daily_aggregates: Dict[str, Dict[str, Any]] = {}

    for entry in entries:
        d_str = entry.entry_date.isoformat()
        if d_str not in daily_aggregates:
            daily_aggregates[d_str] = {
                "date": d_str,
                "calories": 0.0,
                "protein_g": 0.0,
                "carbs_g": 0.0,
                "fat_g": 0.0,
                "iron_mg": 0.0,
                "calcium_mg": 0.0,
                "vitamin_d_mcg": 0.0,
                "vitamin_b12_mcg": 0.0,
                "items_count": 0,
            }

        food = entry.food
        qty = float(entry.quantity or 1.0)
        if food:
            daily_aggregates[d_str]["calories"] += float(food.calories or 0.0) * qty
            daily_aggregates[d_str]["protein_g"] += float(food.protein_g or 0.0) * qty
            daily_aggregates[d_str]["carbs_g"] += float(food.carbs_g or 0.0) * qty
            daily_aggregates[d_str]["fat_g"] += float(food.fat_g or 0.0) * qty
            daily_aggregates[d_str]["iron_mg"] += float(food.iron_mg or 0.0) * qty
            daily_aggregates[d_str]["calcium_mg"] += float(food.calcium_mg or 0.0) * qty
            daily_aggregates[d_str]["vitamin_d_mcg"] += float(food.vitamin_d_mcg or 0.0) * qty
            daily_aggregates[d_str]["vitamin_b12_mcg"] += float(food.vitamin_b12_mcg or 0.0) * qty
            daily_aggregates[d_str]["items_count"] += 1

    trends = sorted(daily_aggregates.values(), key=lambda x: x["date"])

    # Baseline adherence check
    for item in trends:
        item["calories"] = round(item["calories"])
        item["protein_g"] = round(item["protein_g"], 1)
        item["carbs_g"] = round(item["carbs_g"], 1)
        item["fat_g"] = round(item["fat_g"], 1)
        item["iron_mg"] = round(item["iron_mg"], 1)
        item["calcium_mg"] = round(item["calcium_mg"], 1)
        item["vitamin_d_mcg"] = round(item["vitamin_d_mcg"], 1)
        item["vitamin_b12_mcg"] = round(item["vitamin_b12_mcg"], 1)
        # Adherence score calculation based on target baseline (~2000 kcal)
        item["adherence_score"] = min(100, round((item["calories"] / 2000) * 100))

    if len(trends) < 2:
        return {
            "has_sufficient_data": False,
            "message": "Insufficient historical entries. Log meals for at least 2 distinct days to unlock trend analytics.",
            "days_recorded": len(trends),
            "trends": trends,
        }

    return {
        "has_sufficient_data": True,
        "days_recorded": len(trends),
        "trends": trends,
    } 
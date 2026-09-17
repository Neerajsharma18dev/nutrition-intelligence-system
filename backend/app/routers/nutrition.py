from datetime import date
from typing import List, Optional
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
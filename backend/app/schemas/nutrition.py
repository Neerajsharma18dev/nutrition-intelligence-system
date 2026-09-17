from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class FoodOut(BaseModel):
    id: int
    name: str
    category: str
    serving_description: str
    serving_grams: float
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    iron_mg: float
    calcium_mg: float
    vitamin_d_mcg: float
    vitamin_b12_mcg: float
    vitamin_c_mg: float
    is_vegetarian: bool
    is_vegan: bool
    is_gluten_free: bool
    is_dairy_free: bool

    class Config:
        from_attributes = True


class DiaryEntryCreate(BaseModel):
    food_id: int
    quantity: float = Field(default=1.0, gt=0, description="Servings count")
    meal_type: str = Field(..., description="breakfast | lunch | dinner | snack")
    entry_date: Optional[date] = None


class DiaryEntryOut(BaseModel):
    id: int
    food_id: int
    food: FoodOut
    quantity: float
    meal_type: str
    entry_date: date
    created_at: datetime

    class Config:
        from_attributes = True


class DailyNutritionReport(BaseModel):
    date: date
    totals: dict
    entries: List[DiaryEntryOut]
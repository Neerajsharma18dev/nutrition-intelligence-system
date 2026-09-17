"""
Import every model here so that a single `from app import models` is enough
for SQLAlchemy's Base.metadata to know about all tables.

If a model is not imported in this file, create_all() will silently skip it.
"""

from .analysis import MealPlan, Prediction, ProgressRecord, Recommendation
from .assessment import BloodTest, SymptomAssessment
from .nutrition import Food, FoodDiaryEntry
from .user import HealthProfile, User

__all__ = [
    "User",
    "HealthProfile",
    "Food",
    "FoodDiaryEntry",
    "SymptomAssessment",
    "BloodTest",
    "Prediction",
    "Recommendation",
    "MealPlan",
    "ProgressRecord",
]
"""Food catalogue and the user's food diary."""

from datetime import date, datetime

from sqlalchemy import JSON, Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class Food(Base):
    """
    One catalogue item. All nutrient values are PER SERVING, not per 100 g,
    so the diary can simply multiply by the number of servings.
    """

    __tablename__ = "foods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(140), nullable=False, index=True)
    category = Column(String(60), nullable=False)             # grain, protein, vegetable...
    serving_description = Column(String(80), nullable=False)  # "1 cup cooked"
    serving_grams = Column(Float, nullable=False)

    # --- Macronutrients ---
    calories = Column(Float, default=0.0)
    protein_g = Column(Float, default=0.0)
    carbs_g = Column(Float, default=0.0)
    fat_g = Column(Float, default=0.0)
    fiber_g = Column(Float, default=0.0)

    # --- Micronutrients tracked by the ML models ---
    iron_mg = Column(Float, default=0.0)
    calcium_mg = Column(Float, default=0.0)
    vitamin_d_mcg = Column(Float, default=0.0)
    vitamin_b12_mcg = Column(Float, default=0.0)
    vitamin_c_mg = Column(Float, default=0.0)

    # --- Dietary suitability flags, used by the recommendation engine ---
    is_vegetarian = Column(Boolean, default=True)
    is_vegan = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=True)
    is_dairy_free = Column(Boolean, default=True)

    # Meal types this food suits: ["breakfast", "snack"]
    suitable_meals = Column(JSON, default=list)
    tags = Column(JSON, default=list)

    diary_entries = relationship("FoodDiaryEntry", back_populates="food")

    def __repr__(self) -> str:
        return f"<Food id={self.id} name={self.name!r}>"


class FoodDiaryEntry(Base):
    """A single logged food item for one user on one day."""

    __tablename__ = "food_diary"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    food_id = Column(Integer, ForeignKey("foods.id"), nullable=False)

    quantity = Column(Float, default=1.0, nullable=False)   # number of servings
    meal_type = Column(String(20), nullable=False)          # breakfast|lunch|dinner|snack
    entry_date = Column(Date, default=date.today, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="diary_entries")
    food = relationship("Food", back_populates="diary_entries")

    def __repr__(self) -> str:
        return f"<FoodDiaryEntry id={self.id} food_id={self.food_id} qty={self.quantity}>"
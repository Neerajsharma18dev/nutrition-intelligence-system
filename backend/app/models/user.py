"""User account and health profile tables."""

from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class User(Base):
    """A registered account. Passwords are only ever stored hashed."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(120), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_demo = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # --- Relationships (cascade so deleting a user cleans up their data) ---
    profile = relationship(
        "HealthProfile", back_populates="user",
        uselist=False, cascade="all, delete-orphan",
    )
    diary_entries = relationship("FoodDiaryEntry", back_populates="user", cascade="all, delete-orphan")
    symptom_assessments = relationship("SymptomAssessment", back_populates="user", cascade="all, delete-orphan")
    blood_tests = relationship("BloodTest", back_populates="user", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="user", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlan", back_populates="user", cascade="all, delete-orphan")
    progress_records = relationship("ProgressRecord", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"


class HealthProfile(Base):
    """
    Demographic and lifestyle information for one user.

    List-type fields (conditions, restrictions, goals) are stored as JSON so
    the schema does not need extra join tables for a prototype.
    """

    __tablename__ = "health_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)

    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)          # male | female | other
    height_cm = Column(Float, nullable=False)
    weight_kg = Column(Float, nullable=False)
    activity_level = Column(String(20), default="moderate", nullable=False)
    sun_exposure_hours = Column(Float, default=1.0, nullable=False)  # daily avg, drives vitamin D

    medical_conditions = Column(JSON, default=list)      # ["anemia", "hypothyroidism"]
    dietary_restrictions = Column(JSON, default=list)    # ["vegetarian", "gluten_free"]
    health_goals = Column(JSON, default=list)            # ["increase_energy", "weight_loss"]

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="profile")

    @property
    def bmi(self) -> float:
        """Body Mass Index. Returns 0.0 if height is missing to avoid divide-by-zero."""
        if not self.height_cm:
            return 0.0
        height_m = self.height_cm / 100.0
        return round(self.weight_kg / (height_m**2), 1)

    def __repr__(self) -> str:
        return f"<HealthProfile user_id={self.user_id} age={self.age}>"
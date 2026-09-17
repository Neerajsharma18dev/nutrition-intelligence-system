"""ML outputs: predictions, recommendations, meal plans, progress history."""

from datetime import date, datetime

from sqlalchemy import JSON, Column, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class Prediction(Base):
    """
    One run of the deficiency-risk pipeline.

    `results` holds the full structured output as JSON, e.g.:
        [{"nutrient": "vitamin_d", "risk_level": "high", "risk_percentage": 78.4,
          "confidence": 0.82, "explanation": "...", "contributing_factors": {...}}, ...]
    Storing JSON keeps the schema stable while the ML output format evolves.
    """

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    model_version = Column(String(40), default="rf-v1", nullable=False)
    overall_score = Column(Float, default=0.0)   # 0-100 composite nutrition status score
    results = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="predictions")
    recommendations = relationship(
        "Recommendation", back_populates="prediction", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Prediction id={self.id} user_id={self.user_id} score={self.overall_score}>"


class Recommendation(Base):
    """Food recommendations generated for one nutrient risk."""

    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=True)

    nutrient = Column(String(40), nullable=False)
    # payload = {"foods": [...], "serving_suggestions": [...], "meal_types": [...]}
    payload = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    prediction = relationship("Prediction", back_populates="recommendations")

    def __repr__(self) -> str:
        return f"<Recommendation id={self.id} nutrient={self.nutrient!r}>"


class MealPlan(Base):
    """A generated 7-day meal plan stored as JSON."""

    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    start_date = Column(Date, default=date.today, nullable=False)
    generated_from_prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=True)

    # plan = [{"day": 1, "date": "...", "meals": {"breakfast": [...], ...},
    #          "daily_totals": {...}}, ...]
    plan = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="meal_plans")

    def __repr__(self) -> str:
        return f"<MealPlan id={self.id} start={self.start_date}>"


class ProgressRecord(Base):
    """
    One nutrient's risk score on one date. The progress chart queries this
    table filtered by week window (4 / 8 / 12 weeks).
    """

    __tablename__ = "progress_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    record_date = Column(Date, default=date.today, nullable=False, index=True)
    week_index = Column(Integer, default=0, nullable=False)

    nutrient = Column(String(40), nullable=False)
    risk_score = Column(Float, default=0.0)          # 0-100
    intake_adherence = Column(Float, default=0.0)    # % of RDA met that week

    user = relationship("User", back_populates="progress_records")

    def __repr__(self) -> str:
        return f"<ProgressRecord {self.nutrient} {self.record_date} {self.risk_score}>"
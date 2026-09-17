from datetime import datetime
from typing import Any, Dict, List
from pydantic import BaseModel


class FactorExplanation(BaseModel):
    feature: str
    label: str
    impact: float
    direction: str


class NutrientRisk(BaseModel):
    nutrient: str
    risk_percentage: float
    risk_level: str
    confidence: float
    top_factors: List[FactorExplanation]


class PredictionResponse(BaseModel):
    prediction_id: int
    overall_score: float
    created_at: datetime
    results: List[NutrientRisk]

    class Config:
        from_attributes = True
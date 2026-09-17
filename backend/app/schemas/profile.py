from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class HealthProfileBase(BaseModel):
    age: int = Field(..., ge=1, le=120, description="Age between 1 and 120")
    gender: str = Field(..., description="male | female | other")
    height_cm: float = Field(..., ge=50.0, le=260.0, description="Height in cm")
    weight_kg: float = Field(..., ge=20.0, le=350.0, description="Weight in kg")
    activity_level: str = Field(default="moderate", description="sedentary | light | moderate | active | very_active")
    sun_exposure_hours: float = Field(default=1.0, ge=0.0, le=24.0)
    medical_conditions: List[str] = Field(default_factory=list)
    dietary_restrictions: List[str] = Field(default_factory=list)
    health_goals: List[str] = Field(default_factory=list)


class HealthProfileCreateUpdate(HealthProfileBase):
    pass


class HealthProfileOut(HealthProfileBase):
    id: int
    user_id: int
    bmi: float
    updated_at: datetime

    class Config:
        from_attributes = True
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class SymptomCreate(BaseModel):
    assessment_date: Optional[date] = None
    fatigue: int = Field(0, ge=0, le=3)
    hair_loss: int = Field(0, ge=0, le=3)
    skin_problems: int = Field(0, ge=0, le=3)
    muscle_weakness: int = Field(0, ge=0, le=3)
    mood_changes: int = Field(0, ge=0, le=3)
    brittle_nails: int = Field(0, ge=0, le=3)
    pale_skin: int = Field(0, ge=0, le=3)
    frequent_infections: int = Field(0, ge=0, le=3)
    poor_concentration: int = Field(0, ge=0, le=3)
    bone_joint_pain: int = Field(0, ge=0, le=3)
    numbness_tingling: int = Field(0, ge=0, le=3)
    bleeding_gums: int = Field(0, ge=0, le=3)
    notes: Optional[str] = None


class SymptomOut(SymptomCreate):
    id: int
    user_id: int
    assessment_date: date
    created_at: datetime

    class Config:
        from_attributes = True


class BloodTestCreate(BaseModel):
    test_date: Optional[date] = None
    hemoglobin_g_dl: Optional[float] = None
    vitamin_d_ng_ml: Optional[float] = None
    vitamin_b12_pg_ml: Optional[float] = None
    ferritin_ng_ml: Optional[float] = None
    calcium_mg_dl: Optional[float] = None
    source: str = "manual"


class BloodTestOut(BloodTestCreate):
    id: int
    user_id: int
    test_date: date
    created_at: datetime

    class Config:
        from_attributes = True
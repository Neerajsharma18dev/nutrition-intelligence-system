"""
Feature builder: extracts user profile, dietary history, symptoms,
and blood labs to assemble the exact 31-column vector required by the ML models.
"""

from datetime import date, timedelta
from typing import Optional
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from ..models.assessment import BloodTest, SymptomAssessment
from ..models.nutrition import FoodDiaryEntry
from ..models.user import HealthProfile, User
from .nutrition_calculator import calculate_daily_nutrition

# 31 Columns exact order
ORDERED_COLUMNS = [
    "age",
    "gender_encoded",
    "bmi",
    "activity_level_encoded",
    "sun_exposure_hours",
    "is_vegetarian",
    "iron_intake_pct_rda",
    "calcium_intake_pct_rda",
    "vit_d_intake_pct_rda",
    "b12_intake_pct_rda",
    "vit_c_intake_pct_rda",
    "protein_pct_rda",
    "fiber_pct_rda",
    "fatigue",
    "hair_loss",
    "skin_problems",
    "muscle_weakness",
    "mood_changes",
    "brittle_nails",
    "pale_skin",
    "frequent_infections",
    "poor_concentration",
    "bone_joint_pain",
    "numbness_tingling",
    "bleeding_gums",
    "hemoglobin_g_dl",
    "vitamin_d_ng_ml",
    "vitamin_b12_pg_ml",
    "ferritin_ng_ml",
    "calcium_mg_dl",
    "labs_available",
]

RDA_MAP = {
    "male": {
        "iron": 8.0, "calcium": 1000.0, "vitamin_d": 15.0,
        "vitamin_b12": 2.4, "vitamin_c": 90.0, "protein": 56.0, "fiber": 38.0
    },
    "female": {
        "iron": 18.0, "calcium": 1000.0, "vitamin_d": 15.0,
        "vitamin_b12": 2.4, "vitamin_c": 75.0, "protein": 46.0, "fiber": 25.0
    },
    "other": {
        "iron": 14.0, "calcium": 1000.0, "vitamin_d": 15.0,
        "vitamin_b12": 2.4, "vitamin_c": 85.0, "protein": 50.0, "fiber": 30.0
    },
}

GENDER_ENCODING = {"male": 0, "female": 1, "other": 2}
ACTIVITY_ENCODING = {"sedentary": 0, "light": 1, "moderate": 2, "active": 3, "very_active": 3}


def build_user_feature_vector(user_id: int, db: Session) -> pd.DataFrame:
    """Assembles a 1-row DataFrame containing all 31 features for the ML models."""
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == user_id).first()
    if not profile:
        raise ValueError("User must complete their health profile before running predictions.")

    gender = (profile.gender or "other").lower()
    rdas = RDA_MAP.get(gender, RDA_MAP["other"])

    # 1. Demographics
    age = profile.age
    gender_enc = GENDER_ENCODING.get(gender, 2)
    bmi = profile.bmi
    act_enc = ACTIVITY_ENCODING.get((profile.activity_level or "moderate").lower(), 2)
    sun_hours = profile.sun_exposure_hours or 1.0
    is_veg = 1 if "vegetarian" in [r.lower() for r in (profile.dietary_restrictions or [])] else 0

    # 2. Dietary intake: Last 7 days average
    seven_days_ago = date.today() - timedelta(days=7)
    diary_entries = (
        db.query(FoodDiaryEntry)
        .filter(FoodDiaryEntry.user_id == user_id, FoodDiaryEntry.entry_date >= seven_days_ago)
        .all()
    )

    logged_days = len(set(e.entry_date for e in diary_entries)) or 1
    totals = calculate_daily_nutrition(diary_entries)

    # % of RDA
    iron_pct = min((totals["iron_mg"] / logged_days) / rdas["iron"], 2.5)
    calcium_pct = min((totals["calcium_mg"] / logged_days) / rdas["calcium"], 2.5)
    vit_d_pct = min((totals["vitamin_d_mcg"] / logged_days) / rdas["vitamin_d"], 2.5)
    b12_pct = min((totals["vitamin_b12_mcg"] / logged_days) / rdas["vitamin_b12"], 2.5)
    vit_c_pct = min((totals["vitamin_c_mg"] / logged_days) / rdas["vitamin_c"], 2.5)
    protein_pct = min((totals["protein_g"] / logged_days) / rdas["protein"], 2.5)
    fiber_pct = min((totals["fiber_g"] / logged_days) / rdas["fiber"], 2.5)

    # 3. Latest Symptoms
    symptoms = (
        db.query(SymptomAssessment)
        .filter(SymptomAssessment.user_id == user_id)
        .order_by(SymptomAssessment.assessment_date.desc(), SymptomAssessment.id.desc())
        .first()
    )

    symp_dict = {
        "fatigue": symptoms.fatigue if symptoms else 0,
        "hair_loss": symptoms.hair_loss if symptoms else 0,
        "skin_problems": symptoms.skin_problems if symptoms else 0,
        "muscle_weakness": symptoms.muscle_weakness if symptoms else 0,
        "mood_changes": symptoms.mood_changes if symptoms else 0,
        "brittle_nails": symptoms.brittle_nails if symptoms else 0,
        "pale_skin": symptoms.pale_skin if symptoms else 0,
        "frequent_infections": symptoms.frequent_infections if symptoms else 0,
        "poor_concentration": symptoms.poor_concentration if symptoms else 0,
        "bone_joint_pain": symptoms.bone_joint_pain if symptoms else 0,
        "numbness_tingling": symptoms.numbness_tingling if symptoms else 0,
        "bleeding_gums": symptoms.bleeding_gums if symptoms else 0,
    }

    # 4. Latest Labs
    labs = (
        db.query(BloodTest)
        .filter(BloodTest.user_id == user_id)
        .order_by(BloodTest.test_date.desc(), BloodTest.id.desc())
        .first()
    )

    labs_available = 1 if labs else 0
    lab_dict = {
        "hemoglobin_g_dl": labs.hemoglobin_g_dl if labs and labs.hemoglobin_g_dl is not None else np.nan,
        "vitamin_d_ng_ml": labs.vitamin_d_ng_ml if labs and labs.vitamin_d_ng_ml is not None else np.nan,
        "vitamin_b12_pg_ml": labs.vitamin_b12_pg_ml if labs and labs.vitamin_b12_pg_ml is not None else np.nan,
        "ferritin_ng_ml": labs.ferritin_ng_ml if labs and labs.ferritin_ng_ml is not None else np.nan,
        "calcium_mg_dl": labs.calcium_mg_dl if labs and labs.calcium_mg_dl is not None else np.nan,
    }

    feature_record = {
        "age": age,
        "gender_encoded": gender_enc,
        "bmi": bmi,
        "activity_level_encoded": act_enc,
        "sun_exposure_hours": sun_hours,
        "is_vegetarian": is_veg,
        "iron_intake_pct_rda": iron_pct,
        "calcium_intake_pct_rda": calcium_pct,
        "vit_d_intake_pct_rda": vit_d_pct,
        "b12_intake_pct_rda": b12_pct,
        "vit_c_intake_pct_rda": vit_c_pct,
        "protein_pct_rda": protein_pct,
        "fiber_pct_rda": fiber_pct,
        **symp_dict,
        **lab_dict,
        "labs_available": labs_available,
    }

    df = pd.DataFrame([feature_record])
    return df[ORDERED_COLUMNS]
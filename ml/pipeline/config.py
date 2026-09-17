"""
ML Pipeline configuration: Feature definitions, target nutrients, and RDA baselines.
"""

TARGET_NUTRIENTS = [
    "iron",
    "vitamin_d",
    "vitamin_b12",
    "calcium",
    "vitamin_c",
]

# Standard Adult Reference Daily Allowances (RDAs)
RDA_STANDARDS = {
    "male": {
        "iron_mg": 8.0,
        "calcium_mg": 1000.0,
        "vitamin_d_mcg": 15.0,
        "vitamin_b12_mcg": 2.4,
        "vitamin_c_mg": 90.0,
        "protein_g": 56.0,
        "fiber_g": 38.0,
    },
    "female": {
        "iron_mg": 18.0,
        "calcium_mg": 1000.0,
        "vitamin_d_mcg": 15.0,
        "vitamin_b12_mcg": 2.4,
        "vitamin_c_mg": 75.0,
        "protein_g": 46.0,
        "fiber_g": 25.0,
    },
    "other": {
        "iron_mg": 14.0,
        "calcium_mg": 1000.0,
        "vitamin_d_mcg": 15.0,
        "vitamin_b12_mcg": 2.4,
        "vitamin_c_mg": 85.0,
        "protein_g": 50.0,
        "fiber_g": 30.0,
    },
}

# Strict 31-column order expected by the ML pipelines
FEATURE_ORDER = [
    # Demographics (6)
    "age",
    "gender_encoded",
    "bmi",
    "activity_level_encoded",
    "sun_exposure_hours",
    "is_vegetarian",
    # Dietary intake % of RDA (7)
    "iron_intake_pct_rda",
    "calcium_intake_pct_rda",
    "vit_d_intake_pct_rda",
    "b12_intake_pct_rda",
    "vit_c_intake_pct_rda",
    "protein_pct_rda",
    "fiber_pct_rda",
    # Symptoms 0-3 (12)
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
    # Lab values (5)
    "hemoglobin_g_dl",
    "vitamin_d_ng_ml",
    "vitamin_b12_pg_ml",
    "ferritin_ng_ml",
    "calcium_mg_dl",
    # Missing indicator flag (1)
    "labs_available",
]
"""
Generate synthetic dataset for multi-target nutritional deficiency classification.
Saved to data/training/synthetic_training_data.csv.
"""

from pathlib import Path
import numpy as np
import pandas as pd

from pipeline.config import FEATURE_ORDER, TARGET_NUTRIENTS

np.random.seed(42)
N_SAMPLES = 6000

ages = np.random.randint(18, 75, size=N_SAMPLES)
genders = np.random.choice([0, 1, 2], size=N_SAMPLES, p=[0.48, 0.48, 0.04])  # 0: male, 1: female, 2: other
bmis = np.round(np.random.normal(25.5, 4.5, size=N_SAMPLES).clip(16.0, 45.0), 1)
activities = np.random.choice([0, 1, 2, 3], size=N_SAMPLES, p=[0.25, 0.35, 0.25, 0.15])
sun_exposure = np.round(np.random.gamma(shape=2.0, scale=0.8, size=N_SAMPLES).clip(0.0, 8.0), 1)
is_veg = np.random.choice([0, 1], size=N_SAMPLES, p=[0.80, 0.20])

# Diet intake (% RDA: 0.1 to 2.5)
iron_pct = np.random.beta(2, 2, size=N_SAMPLES) * 1.8 + 0.1
calc_pct = np.random.beta(2, 2, size=N_SAMPLES) * 1.8 + 0.1
vit_d_pct = np.random.beta(1.5, 2.5, size=N_SAMPLES) * 1.5 + 0.05
b12_pct = np.where(is_veg == 1, np.random.beta(1, 3, size=N_SAMPLES), np.random.beta(2, 2, size=N_SAMPLES)) * 1.6 + 0.1
vit_c_pct = np.random.beta(2, 2, size=N_SAMPLES) * 1.8 + 0.1
protein_pct = np.random.beta(2.5, 2, size=N_SAMPLES) * 1.5 + 0.3
fiber_pct = np.random.beta(2, 2, size=N_SAMPLES) * 1.5 + 0.2

# Symptoms (0 to 3)
fatigue = np.random.choice([0, 1, 2, 3], size=N_SAMPLES, p=[0.4, 0.3, 0.2, 0.1])
hair_loss = np.random.choice([0, 1, 2, 3], size=N_SAMPLES, p=[0.6, 0.25, 0.1, 0.05])
skin_problems = np.random.choice([0, 1, 2, 3], size=N_SAMPLES, p=[0.55, 0.25, 0.15, 0.05])
muscle_weakness = np.random.choice([0, 1, 2, 3], size=N_SAMPLES, p=[0.5, 0.3, 0.15, 0.05])
mood_changes = np.random.choice([0, 1, 2, 3], size=N_SAMPLES, p=[0.5, 0.3, 0.15, 0.05])
brittle_nails = np.random.choice([0, 1, 2, 3], size=N_SAMPLES, p=[0.65, 0.2, 0.1, 0.05])
pale_skin = np.random.choice([0, 1, 2, 3], size=N_SAMPLES, p=[0.7, 0.18, 0.08, 0.04])
frequent_infections = np.random.choice([0, 1, 2, 3], size=N_SAMPLES, p=[0.7, 0.2, 0.07, 0.03])
poor_concentration = np.random.choice([0, 1, 2, 3], size=N_SAMPLES, p=[0.55, 0.25, 0.15, 0.05])
bone_joint_pain = np.random.choice([0, 1, 2, 3], size=N_SAMPLES, p=[0.6, 0.25, 0.1, 0.05])
numbness_tingling = np.random.choice([0, 1, 2, 3], size=N_SAMPLES, p=[0.75, 0.15, 0.07, 0.03])
bleeding_gums = np.random.choice([0, 1, 2, 3], size=N_SAMPLES, p=[0.8, 0.12, 0.06, 0.02])

# Lab Values (with 35% random missingness)
labs_available = np.random.choice([1, 0], size=N_SAMPLES, p=[0.65, 0.35])

hb = np.where(genders == 0, np.random.normal(15.0, 1.5, size=N_SAMPLES), np.random.normal(13.2, 1.4, size=N_SAMPLES))
vit_d_lab = np.random.normal(32.0, 14.0, size=N_SAMPLES).clip(5.0, 100.0)
b12_lab = np.random.normal(450.0, 180.0, size=N_SAMPLES).clip(80.0, 1100.0)
ferritin_lab = np.random.normal(85.0, 45.0, size=N_SAMPLES).clip(5.0, 350.0)
calcium_lab = np.random.normal(9.4, 0.6, size=N_SAMPLES).clip(7.0, 12.0)

# Apply missingness
hb = np.where(labs_available == 1, hb, np.nan)
vit_d_lab = np.where(labs_available == 1, vit_d_lab, np.nan)
b12_lab = np.where(labs_available == 1, b12_lab, np.nan)
ferritin_lab = np.where(labs_available == 1, ferritin_lab, np.nan)
calcium_lab = np.where(labs_available == 1, calcium_lab, np.nan)

# Generate Labels via Clinical Heuristics + Noise
def compute_label(risk_prob: np.ndarray) -> np.ndarray:
    noise = np.random.normal(0, 0.08, size=N_SAMPLES)
    return ((risk_prob + noise) > 0.50).astype(int)

# 1. Iron deficiency risk
iron_risk = (
    0.35 * (iron_pct < 0.65)
    + 0.25 * ((ferritin_lab < 30.0) | (np.isnan(ferritin_lab) & (pale_skin >= 2)))
    + 0.20 * (fatigue >= 2)
    + 0.20 * (brittle_nails >= 2)
)
y_iron = compute_label(iron_risk)

# 2. Vitamin D deficiency risk
vit_d_risk = (
    0.30 * (vit_d_pct < 0.6)
    + 0.35 * ((vit_d_lab < 20.0) | (np.isnan(vit_d_lab) & (sun_exposure < 1.0)))
    + 0.20 * (bone_joint_pain >= 2)
    + 0.15 * (muscle_weakness >= 2)
)
y_vit_d = compute_label(vit_d_risk)

# 3. Vitamin B12 deficiency risk
b12_risk = (
    0.30 * (b12_pct < 0.6)
    + 0.35 * ((b12_lab < 200.0) | (np.isnan(b12_lab) & (is_veg == 1)))
    + 0.20 * (numbness_tingling >= 1)
    + 0.15 * (poor_concentration >= 2)
)
y_b12 = compute_label(b12_risk)

# 4. Calcium deficiency risk
calcium_risk = (
    0.40 * (calc_pct < 0.65)
    + 0.30 * ((calcium_lab < 8.6) | (np.isnan(calcium_lab) & (bone_joint_pain >= 2)))
    + 0.15 * (muscle_weakness >= 2)
    + 0.15 * (brittle_nails >= 2)
)
y_calcium = compute_label(calcium_risk)

# 5. Vitamin C deficiency risk (diet + symptoms only, no lab)
vit_c_risk = (
    0.50 * (vit_c_pct < 0.6)
    + 0.25 * (bleeding_gums >= 1)
    + 0.15 * (skin_problems >= 2)
    + 0.10 * (frequent_infections >= 2)
)
y_vit_c = compute_label(vit_c_risk)

df = pd.DataFrame({
    "age": ages,
    "gender_encoded": genders,
    "bmi": bmis,
    "activity_level_encoded": activities,
    "sun_exposure_hours": sun_exposure,
    "is_vegetarian": is_veg,
    "iron_intake_pct_rda": np.round(iron_pct, 3),
    "calcium_intake_pct_rda": np.round(calc_pct, 3),
    "vit_d_intake_pct_rda": np.round(vit_d_pct, 3),
    "b12_intake_pct_rda": np.round(b12_pct, 3),
    "vit_c_intake_pct_rda": np.round(vit_c_pct, 3),
    "protein_pct_rda": np.round(protein_pct, 3),
    "fiber_pct_rda": np.round(fiber_pct, 3),
    "fatigue": fatigue,
    "hair_loss": hair_loss,
    "skin_problems": skin_problems,
    "muscle_weakness": muscle_weakness,
    "mood_changes": mood_changes,
    "brittle_nails": brittle_nails,
    "pale_skin": pale_skin,
    "frequent_infections": frequent_infections,
    "poor_concentration": poor_concentration,
    "bone_joint_pain": bone_joint_pain,
    "numbness_tingling": numbness_tingling,
    "bleeding_gums": bleeding_gums,
    "hemoglobin_g_dl": np.round(hb, 2),
    "vitamin_d_ng_ml": np.round(vit_d_lab, 2),
    "vitamin_b12_pg_ml": np.round(b12_lab, 2),
    "ferritin_ng_ml": np.round(ferritin_lab, 2),
    "calcium_mg_dl": np.round(calcium_lab, 2),
    "labs_available": labs_available,
    "target_iron": y_iron,
    "target_vitamin_d": y_vit_d,
    "target_vitamin_b12": y_b12,
    "target_calcium": y_calcium,
    "target_vitamin_c": y_vit_c,
})

out_dir = Path(__file__).resolve().parent.parent / "data" / "training"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "synthetic_training_data.csv"
df.to_csv(out_path, index=False)
print(f"Generated {len(df)} samples -> {out_path}")
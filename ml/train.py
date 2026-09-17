"""
Train 5 Random Forest Classifiers on synthetic dataset and save pipeline artifacts.
"""

import json
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from pipeline.config import FEATURE_ORDER, TARGET_NUTRIENTS

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "training" / "synthetic_training_data.csv"
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

if not DATA_PATH.exists():
    raise FileNotFoundError(f"Training data not found at {DATA_PATH}. Run generate_dataset.py first.")

df = pd.read_csv(DATA_PATH)
X = df[FEATURE_ORDER]

metrics_summary = {}

print(f"Training on {len(df)} samples across 31 features...")

for nutrient in TARGET_NUTRIENTS:
    target_col = f"target_{nutrient}"
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("rf", RandomForestClassifier(
            n_estimators=300,
            max_depth=12,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )),
    ])

    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)
    y_prob = pipe.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    auc = roc_auc_score(y_test, y_prob)

    metrics_summary[nutrient] = {
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1": round(float(f1), 4),
        "roc_auc": round(float(auc), 4),
    }

    model_path = MODELS_DIR / f"rf_{nutrient}.joblib"
    joblib.dump(pipe, model_path)
    print(f"[{nutrient}] F1: {f1:.3f} | AUC: {auc:.3f} -> Saved {model_path.name}")

# Save metrics report
metrics_path = MODELS_DIR / "metrics.json"
with open(metrics_path, "w", encoding="utf-8") as f:
    json.dump(metrics_summary, f, indent=2)

print(f"\nAll models saved. Evaluation metrics stored at: {metrics_path}")
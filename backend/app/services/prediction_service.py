"""
Prediction Service: Loads artifacts, computes multi-nutrient risks,
and attaches SHAP explanations.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List
import joblib
from sqlalchemy.orm import Session

from ..config import MODELS_DIR, PROJECT_ROOT
from ..models.analysis import Prediction
from .feature_builder import build_user_feature_vector

# Ensure ml module is importable
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from ml.explain import ModelExplainer  # noqa: E402

TARGET_NUTRIENTS = ["iron", "vitamin_d", "vitamin_b12", "calcium", "vitamin_c"]


class PredictionEngine:
    _models: Dict[str, Any] = {}
    _explainers: Dict[str, ModelExplainer] = {}

    @classmethod
    def load_artifacts(cls):
        """Loads trained pipelines from disk once on demand."""
        if not cls._models:
            for nutrient in TARGET_NUTRIENTS:
                model_file = Path(MODELS_DIR) / f"rf_{nutrient}.joblib"
                if not model_file.exists():
                    raise FileNotFoundError(f"Model artifact {model_file} not found. Run ml/train.py first.")
                pipe = joblib.load(model_file)
                cls._models[nutrient] = pipe
                cls._explainers[nutrient] = ModelExplainer(pipe)

    @classmethod
    def run_prediction(cls, user_id: int, db: Session) -> Dict[str, Any]:
        cls.load_artifacts()
        X_df = build_user_feature_vector(user_id, db)

        nutrient_results: List[Dict[str, Any]] = []
        overall_risk_sum = 0.0

        for nutrient in TARGET_NUTRIENTS:
            pipe = cls._models[nutrient]
            explainer = cls._explainers[nutrient]

            prob = float(pipe.predict_proba(X_df)[0, 1])
            risk_pct = round(prob * 100, 1)
            overall_risk_sum += risk_pct

            # Determine risk category
            if risk_pct >= 65.0:
                risk_level = "high"
            elif risk_pct >= 35.0:
                risk_level = "moderate"
            else:
                risk_level = "low"

            confidence = round(abs(prob - 0.5) * 2, 2)
            top_factors = explainer.explain_sample(X_df)

            nutrient_results.append({
                "nutrient": nutrient,
                "risk_percentage": risk_pct,
                "risk_level": risk_level,
                "confidence": confidence,
                "top_factors": top_factors,
            })

        composite_score = round(max(0.0, 100.0 - (overall_risk_sum / len(TARGET_NUTRIENTS))), 1)

        # Save record to Database
        prediction_record = Prediction(
            user_id=user_id,
            model_version="rf-v1",
            overall_score=composite_score,
            results=nutrient_results,
        )
        db.add(prediction_record)
        db.commit()
        db.refresh(prediction_record)

        return {
            "prediction_id": prediction_record.id,
            "overall_score": composite_score,
            "created_at": prediction_record.created_at,
            "results": nutrient_results,
        }
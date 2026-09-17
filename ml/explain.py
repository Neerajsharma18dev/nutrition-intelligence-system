"""
SHAP explainability service: unpacks trained tree-based decisions
into plain-language risk factors.
"""

from typing import Any, Dict, List
import numpy as np
import shap

FEATURE_HUMAN_NAMES = {
    "iron_intake_pct_rda": "Dietary iron intake",
    "calcium_intake_pct_rda": "Dietary calcium intake",
    "vit_d_intake_pct_rda": "Dietary vitamin D intake",
    "b12_intake_pct_rda": "Dietary vitamin B12 intake",
    "vit_c_intake_pct_rda": "Dietary vitamin C intake",
    "sun_exposure_hours": "Daily sun exposure",
    "fatigue": "Reported fatigue level",
    "pale_skin": "Reported pale skin",
    "brittle_nails": "Reported brittle nails",
    "muscle_weakness": "Reported muscle weakness",
    "bone_joint_pain": "Reported bone or joint pain",
    "numbness_tingling": "Reported numbness/tingling sensation",
    "bleeding_gums": "Reported bleeding gums",
    "ferritin_ng_ml": "Ferritin blood level",
    "hemoglobin_g_dl": "Hemoglobin level",
    "vitamin_d_ng_ml": "Serum Vitamin D lab result",
    "vitamin_b12_pg_ml": "Serum Vitamin B12 lab result",
    "calcium_mg_dl": "Serum Calcium lab result",
}


class ModelExplainer:
    def __init__(self, model_pipeline: Any):
        self.imputer = model_pipeline.named_steps["imputer"]
        self.rf = model_pipeline.named_steps["rf"]
        self.explainer = shap.TreeExplainer(self.rf)

    def explain_sample(self, X_df) -> List[Dict[str, Any]]:
        """Computes top SHAP positive and negative feature contributions."""
        X_imputed = self.imputer.transform(X_df)
        shap_values = self.explainer.shap_values(X_imputed)

        # For binary classification, shap_values can be list of 2 arrays or 3D array
        if isinstance(shap_values, list):
            sv = shap_values[1][0]
        elif len(shap_values.shape) == 3:
            sv = shap_values[0, :, 1]
        else:
            sv = shap_values[0]

        feature_names = list(X_df.columns)
        contributions = []
        for name, score in zip(feature_names, sv):
            contributions.append({
                "feature": name,
                "label": FEATURE_HUMAN_NAMES.get(name, name.replace("_", " ").title()),
                "impact": float(score),
                "direction": "increased_risk" if score > 0 else "decreased_risk"
            })

        # Sort by absolute contribution strength
        contributions.sort(key=lambda x: abs(x["impact"]), reverse=True)
        return contributions[:5]
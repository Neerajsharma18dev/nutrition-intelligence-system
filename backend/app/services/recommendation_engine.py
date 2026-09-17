"""
Recommendation engine: matches predicted deficiency risks with suitable
nutrient-dense foods respecting dietary restrictions.
"""

from typing import Any, Dict, List
from sqlalchemy.orm import Session

from ..models.analysis import Recommendation
from ..models.nutrition import Food
from ..models.user import HealthProfile

NUTRIENT_COLUMN_MAP = {
    "iron": "iron_mg",
    "vitamin_d": "vitamin_d_mcg",
    "vitamin_b12": "vitamin_b12_mcg",
    "calcium": "calcium_mg",
    "vitamin_c": "vitamin_c_mg",
}

NUTRIENT_TIPS = {
    "iron": "Pair iron-rich foods with Vitamin C sources to boost absorption.",
    "vitamin_d": "Combine Vitamin D foods with healthy fats to enhance absorption.",
    "vitamin_b12": "For plant-based diets, prioritize fortified foods or consult about supplementation.",
    "calcium": "Spread calcium intake across meals rather than consuming it all at once.",
    "vitamin_c": "Consume raw or lightly steamed vegetables; excessive heat destroys Vitamin C.",
}


def generate_recommendations_for_user(
    user_id: int,
    prediction_id: int,
    prediction_results: List[Dict[str, Any]],
    db: Session,
) -> List[Dict[str, Any]]:
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == user_id).first()
    restrictions = [r.lower() for r in (profile.dietary_restrictions if profile else [])]

    db.query(Recommendation).filter(Recommendation.user_id == user_id).delete()

    created_recs = []

    for item in prediction_results:
        nutrient = item["nutrient"]
        risk_level = item["risk_level"]

        if risk_level not in ["moderate", "high"]:
            continue

        col_name = NUTRIENT_COLUMN_MAP.get(nutrient)
        if not col_name:
            continue

        query = db.query(Food).filter(getattr(Food, col_name) > 0)

        if "vegetarian" in restrictions:
            query = query.filter(Food.is_vegetarian == True)
        if "vegan" in restrictions:
            query = query.filter(Food.is_vegan == True)
        if "gluten_free" in restrictions:
            query = query.filter(Food.is_gluten_free == True)
        if "dairy_free" in restrictions:
            query = query.filter(Food.is_dairy_free == True)

        top_foods = query.order_by(getattr(Food, col_name).desc()).limit(6).all()

        food_items = [
            {
                "id": f.id,
                "name": f.name,
                "category": f.category,
                "serving": f.serving_description,
                "nutrient_amount": getattr(f, col_name),
                "calories": f.calories,
            }
            for f in top_foods
        ]

        payload = {
            "risk_level": risk_level,
            "clinical_tip": NUTRIENT_TIPS.get(nutrient, "Focus on nutrient-dense foods."),
            "suggested_foods": food_items,
        }

        rec = Recommendation(
            user_id=user_id,
            prediction_id=prediction_id,
            nutrient=nutrient,
            payload=payload,
        )
        db.add(rec)
        created_recs.append({
            "nutrient": nutrient,
            "risk_level": risk_level,
            "payload": payload,
        })

    db.commit()
    return created_recs
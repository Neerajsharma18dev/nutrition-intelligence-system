from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..core.deps import get_current_user
from ..database import get_db
from ..models.analysis import MealPlan, Prediction, Recommendation
from ..models.user import User
from ..services.meal_planner import generate_7day_meal_plan
from ..services.progress_service import get_user_progress_timeline
from ..services.recommendation_engine import generate_recommendations_for_user

router = APIRouter(prefix="/api", tags=["Recommendations & Planning"])


@router.get("/recommendations")
def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve food recommendations based on the latest prediction."""
    recs = db.query(Recommendation).filter(Recommendation.user_id == current_user.id).all()
    if not recs:
        latest_pred = (
            db.query(Prediction)
            .filter(Prediction.user_id == current_user.id)
            .order_by(Prediction.created_at.desc())
            .first()
        )
        if latest_pred:
            return generate_recommendations_for_user(
                current_user.id, latest_pred.id, latest_pred.results, db
            )
        return []

    return [
        {"nutrient": r.nutrient, "payload": r.payload, "created_at": r.created_at}
        for r in recs
    ]


@router.get("/meal-plan")
def get_current_meal_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch the active 7-day meal plan."""
    plan = (
        db.query(MealPlan)
        .filter(MealPlan.user_id == current_user.id)
        .order_by(MealPlan.created_at.desc())
        .first()
    )
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No meal plan found. Generate one first using /api/meal-plan/regenerate."
        )
    return {"id": plan.id, "start_date": plan.start_date, "plan": plan.plan}


@router.post("/meal-plan/regenerate")
def regenerate_meal_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Build or refresh a 7-day personalized meal plan."""
    latest_pred = (
        db.query(Prediction)
        .filter(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc())
        .first()
    )
    pred_id = latest_pred.id if latest_pred else None
    return generate_7day_meal_plan(user_id=current_user.id, prediction_id=pred_id, db=db)


@router.get("/progress")
def get_progress_data(
    weeks: int = Query(default=8, ge=4, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get weekly risk trajectories for progress charts."""
    return get_user_progress_timeline(user_id=current_user.id, weeks=weeks, db=db)
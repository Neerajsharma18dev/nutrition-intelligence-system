from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.deps import get_current_user
from ..database import get_db
from ..models.analysis import Prediction
from ..models.user import User
from ..schemas.analysis import PredictionResponse
from ..services.prediction_service import PredictionEngine

router = APIRouter(prefix="/api/predict", tags=["AI Prediction & Explainability"])


@router.post("", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
def trigger_prediction(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Execute ML models + SHAP explainer on current user data and persist results."""
    try:
        return PredictionEngine.run_prediction(user_id=current_user.id, db=db)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))


@router.get("/latest", response_model=Optional[PredictionResponse])
def get_latest_prediction(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve the most recent prediction generated for the authenticated user."""
    rec = (
        db.query(Prediction)
        .filter(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc(), Prediction.id.desc())
        .first()
    )
    if not rec:
        return None
    return {
        "prediction_id": rec.id,
        "overall_score": rec.overall_score,
        "created_at": rec.created_at,
        "results": rec.results,
    }
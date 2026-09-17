from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.deps import get_current_user
from ..database import get_db
from ..models.assessment import BloodTest, SymptomAssessment
from ..models.user import User
from ..schemas.assessment import BloodTestCreate, BloodTestOut, SymptomCreate, SymptomOut

router = APIRouter(prefix="/api", tags=["Assessment (Symptoms & Blood)"])


@router.post("/symptoms", response_model=SymptomOut, status_code=status.HTTP_201_CREATED)
def submit_symptoms(
    symptom_in: SymptomCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit symptom evaluation questionnaire."""
    data = symptom_in.model_dump()
    if not data.get("assessment_date"):
        data["assessment_date"] = date.today()

    record = SymptomAssessment(user_id=current_user.id, **data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/symptoms/latest", response_model=Optional[SymptomOut])
def get_latest_symptoms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve the most recent symptom assessment."""
    return (
        db.query(SymptomAssessment)
        .filter(SymptomAssessment.user_id == current_user.id)
        .order_by(SymptomAssessment.assessment_date.desc(), SymptomAssessment.id.desc())
        .first()
    )


@router.post("/blood-tests", response_model=BloodTestOut, status_code=status.HTTP_201_CREATED)
def submit_blood_test(
    test_in: BloodTestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit lab blood test values."""
    data = test_in.model_dump()
    if not data.get("test_date"):
        data["test_date"] = date.today()

    record = BloodTest(user_id=current_user.id, **data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/blood-tests/latest", response_model=Optional[BloodTestOut])
def get_latest_blood_test(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve the most recent blood test report."""
    return (
        db.query(BloodTest)
        .filter(BloodTest.user_id == current_user.id)
        .order_by(BloodTest.test_date.desc(), BloodTest.id.desc())
        .first()
    )
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.deps import get_current_user
from ..database import get_db
from ..models.user import HealthProfile, User
from ..schemas.profile import HealthProfileCreateUpdate, HealthProfileOut

router = APIRouter(prefix="/api/profile", tags=["Health Profile"])


@router.get("", response_model=HealthProfileOut)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetch the health profile for the current user."""
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health profile not found for this user."
        )
    return profile


@router.put("", response_model=HealthProfileOut)
def create_or_update_profile(
    profile_in: HealthProfileCreateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update health profile for the current user."""
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == current_user.id).first()

    data = profile_in.model_dump()

    if not profile:
        profile = HealthProfile(user_id=current_user.id, **data)
        db.add(profile)
    else:
        for field, value in data.items():
            setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile
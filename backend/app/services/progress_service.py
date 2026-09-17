"""
Progress service: tracks risk score trajectories over weeks.
"""

from datetime import date, timedelta
from typing import Any, Dict, List
from sqlalchemy.orm import Session

from ..models.analysis import ProgressRecord


def get_user_progress_timeline(user_id: int, weeks: int, db: Session) -> List[Dict[str, Any]]:
    cutoff_date = date.today() - timedelta(weeks=weeks)
    records = (
        db.query(ProgressRecord)
        .filter(ProgressRecord.user_id == user_id, ProgressRecord.record_date >= cutoff_date)
        .order_by(ProgressRecord.record_date.asc())
        .all()
    )

    return [
        {
            "record_date": str(r.record_date),
            "week_index": r.week_index,
            "nutrient": r.nutrient,
            "risk_score": r.risk_score,
            "intake_adherence": r.intake_adherence,
        }
        for r in records
    ]
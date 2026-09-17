"""Symptom questionnaires and blood test results."""

from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class SymptomAssessment(Base):
    """
    One completed symptom questionnaire.

    Every symptom uses the same 0-3 severity scale:
        0 = None, 1 = Mild, 2 = Moderate, 3 = Severe
    These twelve items are common non-specific indicators discussed in
    nutrition literature. They are screening inputs, NOT diagnostic criteria.
    """

    __tablename__ = "symptom_assessments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    assessment_date = Column(Date, default=date.today, nullable=False, index=True)

    fatigue = Column(Integer, default=0, nullable=False)
    hair_loss = Column(Integer, default=0, nullable=False)
    skin_problems = Column(Integer, default=0, nullable=False)
    muscle_weakness = Column(Integer, default=0, nullable=False)
    mood_changes = Column(Integer, default=0, nullable=False)
    brittle_nails = Column(Integer, default=0, nullable=False)
    pale_skin = Column(Integer, default=0, nullable=False)
    frequent_infections = Column(Integer, default=0, nullable=False)
    poor_concentration = Column(Integer, default=0, nullable=False)
    bone_joint_pain = Column(Integer, default=0, nullable=False)
    numbness_tingling = Column(Integer, default=0, nullable=False)
    bleeding_gums = Column(Integer, default=0, nullable=False)

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="symptom_assessments")

    def __repr__(self) -> str:
        return f"<SymptomAssessment id={self.id} date={self.assessment_date}>"


class BloodTest(Base):
    """
    Laboratory values entered by the user.

    All value columns are nullable on purpose: a user may have only a partial
    panel, and the ML pipeline handles missing labs via imputation plus a
    'labs_available' indicator feature.
    """

    __tablename__ = "blood_tests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    test_date = Column(Date, default=date.today, nullable=False, index=True)

    hemoglobin_g_dl = Column(Float, nullable=True)      # typical adult range ~12-17 g/dL
    vitamin_d_ng_ml = Column(Float, nullable=True)      # 25-OH vitamin D, ~30-100 ng/mL
    vitamin_b12_pg_ml = Column(Float, nullable=True)    # ~200-900 pg/mL
    ferritin_ng_ml = Column(Float, nullable=True)       # iron store marker, ~30-300 ng/mL
    calcium_mg_dl = Column(Float, nullable=True)        # ~8.5-10.5 mg/dL

    source = Column(String(20), default="manual", nullable=False)  # manual | upload
    uploaded_filename = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="blood_tests")

    def __repr__(self) -> str:
        return f"<BloodTest id={self.id} date={self.test_date} source={self.source}>"
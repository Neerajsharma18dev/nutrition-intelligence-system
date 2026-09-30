"""
FastAPI application entrypoint.
Updated for Milestone 3: Integrated 7-Day Meal Planner & Recommendation Engine.
"""

from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import models  # noqa: F401
from .config import settings
from .database import Base, engine
from .routers import assessment, auth, nutrition, prediction, profile, recommendations
from .services.recommendation_service import RecommendationEngine

ACADEMIC_DISCLAIMER = (
    "This system is an academic research prototype for educational purposes only. "
    "It does not provide medical diagnosis, treatment, or clinical advice. "
    "Predictions are produced by models trained on synthetic demonstration data "
    "and are not clinically validated. Always consult a qualified healthcare "
    "professional regarding health concerns."
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print(f"[startup] Database ready at: {settings.DATABASE_URL}")
    print(f"[startup] Tables: {', '.join(sorted(Base.metadata.tables.keys()))}")
    yield
    print("[shutdown] Application stopped.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Backend API for an MSc Data Science prototype that estimates "
        "nutritional deficiency risk and generates personalised dietary "
        "recommendations.\n\n"
        f"**Disclaimer:** {ACADEMIC_DISCLAIMER}"
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect All Standard Routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(nutrition.router)
app.include_router(assessment.router)
app.include_router(prediction.router)
app.include_router(recommendations.router)


# --- Milestone 3 Pydantic Schemas ---
class MealPlanRequest(BaseModel):
    detected_deficiencies: List[str] = Field(
        default_factory=list,
        example=["iron_deficiency_anemia", "vitamin_d_deficiency"]
    )
    diet_preference: str = Field(default="vegetarian", example="vegetarian")
    allergies: List[str] = Field(default_factory=list, example=["nuts"])


class MealSwapRequest(BaseModel):
    current_food_id: str = Field(..., example="food_2")
    meal_slot: str = Field(..., example="breakfast")
    diet_preference: str = Field(default="vegetarian", example="vegetarian")
    allergies: List[str] = Field(default_factory=list, example=["nuts"])
    detected_deficiencies: List[str] = Field(default_factory=list)


# --- System Endpoints ---
@app.get("/", tags=["System"])
def root():
    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "documentation": "/docs",
        "disclaimer": ACADEMIC_DISCLAIMER,
    }


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "database": "connected"}


@app.get("/api/system/tables", tags=["System"])
def list_tables():
    return {"tables": sorted(Base.metadata.tables.keys())}


# --- Milestone 3: Direct Recommendation & Meal Planner Endpoints ---
@app.post(
    "/api/v1/recommendations/generate-plan",
    tags=["Milestone 3 - Meal Planner"],
    summary="Generate a personalized 7-day meal plan based on detected risks"
)
def generate_meal_plan(payload: MealPlanRequest):
    """
    Generates a 7-day schedule (breakfast, lunch, snack, dinner)
    prioritizing foods addressing detected risks while strictly filtering
    allergens and dietary preferences.
    """
    try:
        plan_data = RecommendationEngine.generate_7_day_meal_plan(
            detected_deficiencies=payload.detected_deficiencies,
            diet_preference=payload.diet_preference,
            allergies=payload.allergies,
        )
        return {"status": "success", "data": plan_data}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(exc)}")


@app.post(
    "/api/v1/recommendations/swap-meal",
    tags=["Milestone 3 - Meal Planner"],
    summary="Swap an individual meal while maintaining strict dietary/allergy safety"
)
def swap_meal_option(payload: MealSwapRequest):
    """
    Finds alternative safe meal choices for a specific slot,
    ensuring allergies and dietary restrictions are completely preserved.
    """
    try:
        ranked_foods = RecommendationEngine.get_ranked_foods(
            detected_deficiencies=payload.detected_deficiencies,
            diet_preference=payload.diet_preference,
            allergies=payload.allergies,
        )
        # Filter for the same slot excluding current food
        alternatives = [
            f for f in ranked_foods
            if f.get("meal_slot") == payload.meal_slot and f.get("id") != payload.current_food_id
        ]
        return {
            "status": "success",
            "count": len(alternatives),
            "alternatives": alternatives
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Meal swap failed: {str(exc)}") 
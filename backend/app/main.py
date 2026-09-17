"""
FastAPI application entrypoint.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models  # noqa: F401
from .config import settings
from .database import Base, engine
from .routers import assessment, auth, nutrition, prediction, profile, recommendations

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

# Connect All Routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(nutrition.router)
app.include_router(assessment.router)
app.include_router(prediction.router)
app.include_router(recommendations.router)


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
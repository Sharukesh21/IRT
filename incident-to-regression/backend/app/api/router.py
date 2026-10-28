"""Main API router — aggregates all versioned route groups."""

from fastapi import APIRouter

from app.api.routes import health
from app.core.config import get_settings

settings = get_settings()

from fastapi import APIRouter, Depends

from app.api.routes import health
from app.core.config import get_settings
from app.core.security import verify_api_key
from app.core.metrics import router as metrics_router

settings = get_settings()

from app.api.routes import health, exams, students, sessions, failure, incidents, regression, ci, evaluation, dashboard, jobs

api_router = APIRouter(prefix=settings.API_PREFIX, dependencies=[Depends(verify_api_key)])

# Register route groups
api_router.include_router(health.router)
api_router.include_router(metrics_router)
api_router.include_router(exams.router)
api_router.include_router(students.router)
api_router.include_router(sessions.router)
api_router.include_router(failure.router)
api_router.include_router(incidents.router)
api_router.include_router(regression.router)
api_router.include_router(ci.router)
api_router.include_router(evaluation.router)
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
# from app.api.routes.incidents import router as incidents_router
# api_router.include_router(incidents_router)
#
# from app.api.routes.events import router as events_router
# api_router.include_router(events_router)
#
# from app.api.routes.regression_tests import router as regression_router
# api_router.include_router(regression_router)

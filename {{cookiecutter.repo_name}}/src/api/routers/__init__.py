from fastapi import APIRouter

from src.api.routers.openai import router as openai_router
from src.api.routers.status import router as status_router
from src.api.routers.version import router as version_router
from src.api.routers.settings import router as settings_router

# Define main router to register all sub routers
router = APIRouter()
router.include_router(status_router, tags=["status"])
router.include_router(openai_router, tags=["openai"])
router.include_router(version_router, tags=["version"])
router.include_router(settings_router, tags=["settings"])


__all__ = ["router"]

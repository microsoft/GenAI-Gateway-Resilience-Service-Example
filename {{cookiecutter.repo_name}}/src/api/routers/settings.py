from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.dependency_container import DependencyContainer
from src.settings import Settings

router = APIRouter()


@router.get("/settings", response_class=JSONResponse)
@inject
async def settings(settings: Settings = Depends(Provide[DependencyContainer.settings])):
    return settings

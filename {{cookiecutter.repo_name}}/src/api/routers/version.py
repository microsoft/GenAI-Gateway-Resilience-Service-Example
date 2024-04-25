from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from src.dependency_container import DependencyContainer
from src.settings import Settings

router = APIRouter()


@router.get("/version", response_class=PlainTextResponse)
@inject
async def status(settings: Settings = Depends(Provide[DependencyContainer.settings])):
    return settings.app_version

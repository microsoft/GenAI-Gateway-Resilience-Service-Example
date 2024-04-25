from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter()


@router.get("/", response_class=PlainTextResponse)
@router.get("/status", response_class=PlainTextResponse)
async def status():
    return "OK"

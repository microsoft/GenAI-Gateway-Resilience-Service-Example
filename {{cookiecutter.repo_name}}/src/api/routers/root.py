from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter()


@router.get("/", response_class=PlainTextResponse)
@router.post("/", response_class=PlainTextResponse)
@router.put("/", response_class=PlainTextResponse)
@router.delete("/", response_class=PlainTextResponse)
async def root():
    return "OK"

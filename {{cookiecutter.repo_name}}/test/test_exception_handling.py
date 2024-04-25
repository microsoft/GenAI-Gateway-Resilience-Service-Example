import os
from unittest import TestCase

from fastapi import APIRouter, HTTPException

from src.create_app import create_app
from fastapi.testclient import TestClient

router = APIRouter()


@router.get("/http-exception")
async def http_exception():
    raise HTTPException(status_code=500, detail="It's broken")


@router.get("/exception")
async def exception():
    raise Exception("It's broken")


class Test(TestCase):
    def setUp(self):
        os.environ["APPLICATION_INSIGHTS_ENABLED"] = "False"
        os.environ["PRIMARY_OPENAI_HOST"] = "http://primary-host"
        os.environ["PRIMARY_OPENAI_API_KEY"] = "primary_key"
        os.environ["FALLBACK_OPENAI_HOST"] = "http://fallback-host"
        os.environ["FALLBACK_OPENAI_API_KEY"] = "fallback_key"
        self.app = create_app()
        self.client = TestClient(self.app, raise_server_exceptions=False)
        self.app.include_router(router)

    def test_http_exceptions_return_json_response(self):
        response = self.client.get("/http-exception")
        assert response.status_code == 500
        assert response.json() == {"detail": "It's broken"}

    def test_exceptions_return_json_response(self):
        response = self.client.get("/exception")
        assert response.status_code == 500
        assert response.json() == {"detail": "Internal Server Error: It's broken"}

import pytest
from fastapi.testclient import TestClient

from src.create_app import create_app


@pytest.fixture()
def app(monkeypatch):
    monkeypatch.setenv("PRIMARY_OPENAI_HOST", "dummy_host")
    monkeypatch.setenv("FALLBACK_OPENAI_HOST", "fallback_dummy_host")
    monkeypatch.setenv("PRIMARY_OPENAI_API_KEY", "dummy_api_key")
    monkeypatch.setenv("FALLBACK_OPENAI_API_KEY", "fallback_dummy_api_key")
    app = create_app()

    yield app


@pytest.fixture()
def client(app):
    return TestClient(app)


def test_root(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.text == "OK"

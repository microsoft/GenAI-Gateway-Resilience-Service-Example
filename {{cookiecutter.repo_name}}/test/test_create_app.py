import pytest

from src.create_app import create_app


def test_root_raises_exception_given_primary_openai_host_not_set(monkeypatch):
    monkeypatch.setenv("FALLBACK_OPENAI_HOST", "fallback_dummy_host")
    monkeypatch.setenv("PRIMARY_OPENAI_API_KEY", "dummy_api_key")
    monkeypatch.setenv("FALLBACK_OPENAI_API_KEY", "fallback_dummy_api_key")

    with pytest.raises(Exception):
        create_app()


def test_root_raises_exception_given_fallback_openai_host_not_set(monkeypatch):
    monkeypatch.setenv("PRIMARY_OPENAI_HOST", "dummy_host")
    monkeypatch.setenv("PRIMARY_OPENAI_API_KEY", "dummy_api_key")
    monkeypatch.setenv("FALLBACK_OPENAI_API_KEY", "fallback_dummy_api_key")

    with pytest.raises(Exception):
        create_app()


def test_root_raises_exception_given_primary_openai_apikey_not_set(monkeypatch):
    monkeypatch.setenv("PRIMARY_OPENAI_HOST", "dummy_host")
    monkeypatch.setenv("FALLBACK_OPENAI_HOST", "fallback_dummy_host")
    monkeypatch.setenv("FALLBACK_OPENAI_API_KEY", "fallback_dummy_api_key")

    with pytest.raises(Exception):
        create_app()


def test_root_raises_exception_given_fallback_openai_apikey_not_set(monkeypatch):
    monkeypatch.setenv("PRIMARY_OPENAI_HOST", "dummy_host")
    monkeypatch.setenv("FALLBACK_OPENAI_HOST", "fallback_dummy_host")
    monkeypatch.setenv("PRIMARY_OPENAI_API_KEY", "dummy_api_key")

    with pytest.raises(Exception):
        create_app()

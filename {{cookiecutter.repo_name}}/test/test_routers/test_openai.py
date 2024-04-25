import json
import pytest
from unittest.mock import MagicMock, Mock, patch
from fastapi.testclient import TestClient
from pydantic import SecretStr

from src.create_app import create_app
from src.services import CircuitBreakerService

from test.resources import TestBase

primary_openai_host = "http://dummy_host_primary"
fallback_openai_host = "http://dummy_host_fallback"

primary_openai_api_key = "dummy_api_key_primary"
fallback_openai_api_key = "dummy_api_key_fallback"


class Test(TestBase):
    def test_openai_forwards_requests_and_returns_successful_response(self):
        with patch("src.api.routers.openai.requests.request") as request:
            request_data = json.dumps(
                {
                    "messages": [{"role": "system", "content": "Message"}],
                    "model": "gpt-35-turbo",
                    "frequency_penalty": 0.0,
                    "logit_bias": {},
                    "max_tokens": 1000,
                    "n": 1,
                    "presence_penalty": 0.0,
                    "stop": None,
                    "stream": False,
                    "temperature": 0.0,
                    "top_p": 1.0,
                    "user": "",
                }
            )
            response_data = json.dumps(
                {
                    "id": "chatcmpl-8xaBj8LBEkmnqOxVQ4IS2UsRCLmPT",
                    "object": "chat.completion",
                    "created": 1709211151,
                    "model": "gpt-35-turbo",
                    "choices": [
                        {
                            "finish_reason": "stop",
                            "index": 0,
                            "message": {"role": "assistant", "content": "Mock content"},
                            "logprobs": None,
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 1985,
                        "completion_tokens": 150,
                        "total_tokens": 2135,
                    },
                }
            )

            mock_downstream_response = Mock()
            mock_downstream_response.content = bytes(response_data, encoding="utf-8")
            mock_downstream_response.status_code = 200
            mock_downstream_response.headers = {
                "connection": "keep-alive",
                "content-type": "application/json",
            }
            request.return_value = mock_downstream_response
            response = self.client.post(
                "/openai/deployments/gpt-35-turbo/chat/completions?api-version=2023-03-15-preview",
                content=request_data,
            )
            settings = self.app.container.settings()

            assert request.call_args[0] == (
                "POST",
                f"{settings.primary_open_ai_host}/openai/deployments/gpt-35-turbo/chat/completions",
            )
            assert request.call_args[1]["params"] == {
                "api-version": "2023-03-15-preview"
            }
            assert request.call_args[1]["headers"].get("host") == "primary-host"
            assert request.call_args[1]["data"] == bytes(request_data, encoding="utf-8")
            assert response.text == response_data
            assert response.status_code == 200
            assert "connection" not in response.headers


request_data = json.dumps(
    {
        "messages": [{"role": "system", "content": "Message"}],
        "model": "gpt-35-turbo",
        "frequency_penalty": 0.0,
        "logit_bias": {},
        "max_tokens": 1000,
        "n": 1,
        "presence_penalty": 0.0,
        "stop": None,
        "stream": False,
        "temperature": 0.0,
        "top_p": 1.0,
        "user": "",
    }
)
success_response_data = json.dumps(
    {
        "id": "chatcmpl-8xaBj8LBEkmnqOxVQ4IS2UsRCLmPT",
        "object": "chat.completion",
        "created": 1709211151,
        "model": "gpt-35-turbo",
        "choices": [
            {
                "finish_reason": "stop",
                "index": 0,
                "message": {"role": "assistant", "content": "Mock content"},
                "logprobs": None,
            }
        ],
        "usage": {
            "prompt_tokens": 1985,
            "completion_tokens": 150,
            "total_tokens": 2135,
        },
    }
)


@pytest.fixture()
def app(monkeypatch):
    monkeypatch.setenv("PRIMARY_OPENAI_HOST", primary_openai_host)
    monkeypatch.setenv("FALLBACK_OPENAI_HOST", fallback_openai_host)
    monkeypatch.setenv("PRIMARY_OPENAI_API_KEY", primary_openai_api_key)
    monkeypatch.setenv("FALLBACK_OPENAI_API_KEY", fallback_openai_api_key)
    app = create_app()

    yield app


@pytest.fixture()
def client(app):
    return TestClient(app)


async def mock_circuit_breaker_execute(circuit_id, function, fallback_function):
    try:
        return await function()
    except Exception:
        return await fallback_function()


@patch("src.api.routers.openai.requests.request")
def test_openai_bad_request(request: MagicMock, client):
    mock_downstream_response = Mock()
    mock_downstream_response.content = bytes("Bad request", encoding="utf-8")
    mock_downstream_response.status_code = 400
    mock_downstream_response.headers = {
        "connection": "keep-alive",
        "content-type": "application/json",
    }
    settings = client.app.container.settings()
    settings.primary_open_ai_host = primary_openai_host
    settings.secondary_open_ai_host = fallback_openai_host
    request.return_value = mock_downstream_response

    with patch.object(
        CircuitBreakerService, "execute", side_effect=mock_circuit_breaker_execute
    ):
        response = client.post(
            "/openai/deployments/gpt-35-turbo/chat/completions?api-version=2023-03-15-preview",
            content=request_data,
        )

    request.assert_called_once()
    assert request.call_args[0] == (
        "POST",
        f"{primary_openai_host}/openai/deployments/gpt-35-turbo/chat/completions",
    )

    assert response.text == "Bad request"
    assert response.status_code == 400


@patch("src.api.routers.openai.requests.request")
def test_openai_fallbacks_on_exception_calling_primary(request: MagicMock, client):
    mock_downstream_response = Mock()
    mock_downstream_response.content = bytes(success_response_data, encoding="utf-8")
    mock_downstream_response.status_code = 200
    mock_downstream_response.headers = {
        "connection": "keep-alive",
        "content-type": "application/json",
    }

    request.side_effect = [
        Exception("Stubbed primary failure"),
        mock_downstream_response,
    ]

    with patch.object(
        CircuitBreakerService, "execute", side_effect=mock_circuit_breaker_execute
    ):
        response = client.post(
            "/openai/deployments/gpt-35-turbo/chat/"
            "completions?api-version=2023-03-15-preview",
            content=request_data,
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "accept-encoding": "gzip",
                "api-key": "should be replaced",
                "host": "should be replaced",
            },
        )

    # Check first call is still made
    assert request.call_args_list[0][0] == (
        "POST",
        f"{primary_openai_host}/openai/deployments/gpt-35-turbo/chat/completions",
    )

    # Check fallback call is made correctly
    assert request.call_args_list[1][0] == (
        "POST",
        f"{fallback_openai_host}/openai/deployments/gpt-35-turbo/chat/completions",
    )
    assert request.call_args_list[1][1]["params"] == {
        "api-version": "2023-03-15-preview"
    }
    assert request.call_args_list[1][1]["headers"] == {
        "host": "dummy_host_fallback",
        "accept": "application/json",
        "content-type": "application/json",
        "accept-encoding": "gzip",
        "api-key": fallback_openai_api_key,
    }
    assert request.call_args_list[1][1]["data"] == bytes(request_data, encoding="utf-8")

    # Check fallback response is returned
    assert response.text == success_response_data
    assert response.status_code == 200
    assert "connection" not in response.headers
    assert response.headers["content-type"] == "application/json"


@patch("src.api.routers.openai.requests.request")
def test_fallback_after_too_many_requests(request: MagicMock, client):
    mock_downstream_response_one = Mock()
    mock_downstream_response_one.content = bytes("Too many requests", encoding="utf-8")
    mock_downstream_response_one.status_code = 429
    mock_downstream_response_one.headers = {
        "connection": "keep-alive",
        "content-type": "application/json",
    }
    settings = client.app.container.settings()
    settings.primary_open_ai_host = primary_openai_host
    settings.fallback_open_ai_host = fallback_openai_host
    settings.primary_open_ai_api_key = SecretStr(primary_openai_api_key)
    settings.fallback_open_ai_api_key = SecretStr(fallback_openai_api_key)
    mock_downstream_response_two = Mock()
    mock_downstream_response_two.content = bytes(
        success_response_data, encoding="utf-8"
    )
    mock_downstream_response_two.status_code = 200
    mock_downstream_response_two.headers = {
        "connection": "keep-alive",
        "content-type": "application/json",
    }

    request.side_effect = [mock_downstream_response_one, mock_downstream_response_two]

    with patch.object(
        CircuitBreakerService, "execute", side_effect=mock_circuit_breaker_execute
    ):
        response = client.post(
            "/openai/deployments/gpt-35-turbo/chat/completions?api-version=2023-03-15-preview",
            content=request_data,
        )

    assert request.call_count == 2
    assert request.call_args_list[0][0] == (
        "POST",
        f"{primary_openai_host}/openai/deployments/gpt-35-turbo/chat/completions",
    )
    assert request.call_args_list[1][0] == (
        "POST",
        f"{fallback_openai_host}/openai/deployments/gpt-35-turbo/chat/completions",
    )

    assert response.text == success_response_data
    assert response.status_code == 200


@patch("src.api.routers.openai.requests.request")
def test_fallback_failure(request: MagicMock, client):
    mock_downstream_response = Mock()
    mock_downstream_response.content = bytes("Internal server error", encoding="utf-8")
    mock_downstream_response.status_code = 500
    mock_downstream_response.headers = {
        "connection": "keep-alive",
        "content-type": "application/json",
    }
    settings = client.app.container.settings()
    settings.primary_open_ai_host = primary_openai_host
    settings.secondary_open_ai_host = fallback_openai_host
    request.return_value = mock_downstream_response

    with patch.object(
        CircuitBreakerService, "execute", side_effect=mock_circuit_breaker_execute
    ):
        response = client.post(
            "/openai/deployments/gpt-35-turbo/chat/completions?api-version=2023-03-15-preview",
            content=request_data,
        )

    assert request.call_count == 2
    assert request.call_args_list[0][0] == (
        "POST",
        f"{primary_openai_host}/openai/deployments/gpt-35-turbo/chat/completions",
    )
    assert request.call_args_list[1][0] == (
        "POST",
        f"{fallback_openai_host}/openai/deployments/gpt-35-turbo/chat/completions",
    )

    assert response.text == "Internal server error"
    assert response.status_code == 500

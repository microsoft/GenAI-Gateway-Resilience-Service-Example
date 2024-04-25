from pydantic import SecretStr

from src.settings import Settings


class SettingsStub(Settings):
    app_version = "some-fake-version"
    app_insights_enabled = False
    app_insights_connection_string = None
    circuit_failure_threshold = 3
    circuit_retry_timeout = 10
    primary_open_ai_host = "http://primary-host"
    primary_open_ai_api_key = SecretStr("primary_key")
    fallback_open_ai_host = "http://fallback-host"
    fallback_open_ai_api_key = SecretStr("fallback_key")

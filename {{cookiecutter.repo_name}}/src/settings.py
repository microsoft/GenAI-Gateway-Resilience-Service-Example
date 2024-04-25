import os

from pydantic import SecretStr


class Settings:
    def __init__(self):
        self.app_version = os.getenv("APP_VERSION", "UNKNOWN_VERSION")
        app_insights_enabled = os.getenv("APPLICATION_INSIGHTS_ENABLED")
        if app_insights_enabled is not None:
            self.app_insights_enabled = app_insights_enabled.lower() in [
                "true",
                "yes",
                "1",
            ]
        else:
            self.app_insights_enabled = False
        self.app_insights_connection_string: SecretStr = SecretStr(
            os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
        )

        self.circuit_failure_threshold = int(
            os.getenv("CIRCUIT_FAILURE_THRESHOLD", "3")
        )
        self.circuit_retry_timeout = int(os.getenv("CIRCUIT_RETRY_TIMEOUT", "10"))

        self.primary_open_ai_host = os.getenv("PRIMARY_OPENAI_HOST")
        self.primary_open_ai_api_key: SecretStr = SecretStr(
            os.getenv("PRIMARY_OPENAI_API_KEY")
        )
        self.fallback_open_ai_host = os.getenv("FALLBACK_OPENAI_HOST")
        self.fallback_open_ai_api_key: SecretStr = SecretStr(
            os.getenv("FALLBACK_OPENAI_API_KEY")
        )

        # Validate all config vars
        if self.fallback_open_ai_host is None:
            raise Exception("FALLBACK_OPENAI_HOST must be set")

        if self.fallback_open_ai_api_key.get_secret_value() is None:
            raise Exception("FALLBACK_OPENAI_API_KEY must be set")

        if self.primary_open_ai_host is None:
            raise Exception("PRIMARY_OPENAI_HOST must be set")

        if self.primary_open_ai_api_key.get_secret_value() is None:
            raise Exception("PRIMARY_OPENAI_API_KEY must be set")

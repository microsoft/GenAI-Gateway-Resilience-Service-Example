import os
from unittest import TestCase

from fastapi.testclient import TestClient

from src.create_app import create_app

from .stubs import SettingsStub


class TestBase(TestCase):
    def setUp(self):
        os.environ["APP_VERSION"] = "some-fake-version"
        os.environ["APPLICATION_INSIGHTS_ENABLED"] = "False"
        os.environ["PRIMARY_OPENAI_HOST"] = "http://primary-host"
        os.environ["PRIMARY_OPENAI_API_KEY"] = "primary_key"
        os.environ["FALLBACK_OPENAI_HOST"] = "http://fallback-host"
        os.environ["FALLBACK_OPENAI_API_KEY"] = "fallback_key"

        self.app = create_app()
        self.client = TestClient(self.app)
        self.app.container.settings.override(SettingsStub())

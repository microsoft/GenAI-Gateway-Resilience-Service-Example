from test.resources import TestBase
import json


class TestRoot(TestBase):
    def test_settings(self):
        response = self.client.get("/settings")

        expected_settings_response = {
            "app_version": "some-fake-version",
            "app_insights_enabled": False,
            "app_insights_connection_string": "",
            "circuit_failure_threshold": 3,
            "circuit_retry_timeout": 10,
            "primary_open_ai_host": "http://primary-host",
            "primary_open_ai_api_key": "**********",
            "fallback_open_ai_host": "http://fallback-host",
            "fallback_open_ai_api_key": "**********",
        }

        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_settings_response, json.loads(response.text))

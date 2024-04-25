import multiprocessing
import time
from unittest import TestCase
import unittest
import json

import requests
from pytest_httpserver import HTTPServer
from uvicorn import Server, Config

import os
import socket


class UvicornServer(multiprocessing.Process):
    def __init__(self, config: Config):
        super().__init__()
        self.server = Server(config=config)
        self.config = config
        self.port = config.port

    def stop(self):
        self.terminate()

    def run(self, *args, **kwargs):
        self.server.run()


class E2ETests(TestCase):
    app_server: UvicornServer
    primary_mock_server: HTTPServer
    fallback_mock_server: HTTPServer

    @classmethod
    def setUpClass(cls):
        os.environ["NO_PROXY"] = "localhost"
        cls.primary_mock_server = HTTPServer()
        cls.primary_mock_server.start()
        cls.fallback_mock_server = HTTPServer()
        cls.fallback_mock_server.start()
        cls.start_app()

    @classmethod
    def start_app(cls):
        os.environ["APP_VERSION"] = "fake-version-1.0"
        os.environ["PRIMARY_OPENAI_HOST"] = cls.primary_mock_server.url_for("")
        os.environ["FALLBACK_OPENAI_HOST"] = cls.fallback_mock_server.url_for("")
        os.environ["PRIMARY_OPENAI_API_KEY"] = "primary_dummy_api_key"
        os.environ["FALLBACK_OPENAI_API_KEY"] = "fallback_dummy_api_key"
        os.environ["APPLICATION_INSIGHTS_ENABLED"] = "False"

        config = Config(
            "src.main:app", host="0.0.0.0", port=cls._get_free_port(), log_level="debug"
        )
        cls.app_server = UvicornServer(config=config)
        cls.app_server.start()
        cls.wait_for_app()

    @classmethod
    def _get_free_port(cls):
        s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
        s.bind(("localhost", 0))
        address, port = s.getsockname()
        s.close()
        return port

    @classmethod
    def wait_for_app(cls):
        count = 0

        while count < 10:
            try:
                # Send a request to a resource that doesn't exist
                # The app is running if we get a 404
                response = requests.get(f"http://localhost:{cls.app_server.port}/abc")
                if response.status_code == 404:
                    return
            except Exception:
                pass

            count += 1
            time.sleep(5)

        raise Exception("App failed to start")

    @classmethod
    def tearDownClass(cls):
        cls.app_server.terminate()
        cls.primary_mock_server.stop()
        cls.fallback_mock_server.stop()

    def setUp(self):
        self.primary_mock_server.clear()
        self.fallback_mock_server.clear()

    def test_root(self):
        response = requests.get(f"http://localhost:{self.app_server.port}/")

        self.assertEqual(response.content, b"OK")
        self.assertEqual(response.status_code, 200)

    def test_status(self):
        response = requests.get(f"http://localhost:{self.app_server.port}/status")

        self.assertEqual(response.content, b"OK")
        self.assertEqual(response.status_code, 200)

    def test_version(self):
        response = requests.get(f"http://localhost:{self.app_server.port}/version")

        self.assertEqual(response.content, b"fake-version-1.0")
        self.assertEqual(response.status_code, 200)

    def test_settings(self):
        response = requests.get(f"http://localhost:{self.app_server.port}/settings")

        expected_settings = {
            "app_version": "fake-version-1.0",
            "app_insights_enabled": False,
            "app_insights_connection_string": "",
            "circuit_failure_threshold": 3,
            "circuit_retry_timeout": 10,
            "primary_open_ai_host": self.primary_mock_server.url_for(""),
            "primary_open_ai_api_key": "**********",
            "fallback_open_ai_host": self.fallback_mock_server.url_for(""),
            "fallback_open_ai_api_key": "**********",
        }

        self.assertEqual(json.loads(response.text), expected_settings)
        self.assertEqual(response.status_code, 200)

    def test_forwards_get_request(self):
        self.primary_mock_server.expect_request(
            uri="/openai/request",
            method="GET",
            headers={
                "Host": "localhost",
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "Content-Type": "application/json",
                "api-key": "primary_dummy_api_key",
            },
            query_string={"key": "value"},
        ).respond_with_data('{"some": "response"}')

        response = requests.get(
            f"http://localhost:{self.app_server.port}/openai/request",
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "accept-encoding": "gzip",
                "api-key": "should be replaced",
                "host": "should be replaced",
            },
            params={"key": "value"},
        )

        self.assertEqual(response.content, b'{"some": "response"}')
        self.assertEqual(response.status_code, 200)

    def test_forwards_post_request(self):
        self.primary_mock_server.expect_request(
            uri="/openai/request",
            method="POST",
            headers={
                "Host": "localhost",
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "Content-Type": "application/json",
                "api-key": "primary_dummy_api_key",
            },
            query_string={"key": "value"},
            data='{"some": "request"}',
        ).respond_with_data('{"some": "response"}')

        response = requests.post(
            f"http://localhost:{self.app_server.port}/openai/request",
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "accept-encoding": "gzip",
                "api-key": "should be replaced",
                "host": "should be replaced",
            },
            params={"key": "value"},
            data='{"some": "request"}',
        )

        self.assertEqual(response.content, b'{"some": "response"}')
        self.assertEqual(response.status_code, 200)

    def test_calls_fallback_when_primary_fails(self):
        self.primary_mock_server.expect_request(
            uri="/openai/request",
        ).respond_with_data(
            response_data='{"some": "error"}',
            status=500,
        )

        self.fallback_mock_server.expect_request(
            uri="/openai/request",
            method="GET",
            headers={
                "Host": "localhost",
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "Content-Type": "application/json",
                "api-key": "fallback_dummy_api_key",
            },
            query_string={"key": "value"},
        ).respond_with_data('{"some": "fallback response"}')

        response = requests.get(
            f"http://localhost:{self.app_server.port}/openai/request",
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "accept-encoding": "gzip",
                "api-key": "should be replaced",
                "host": "should be replaced",
            },
            params={"key": "value"},
        )

        self.assertEqual(response.content, b'{"some": "fallback response"}')
        self.assertEqual(response.status_code, 200)

    def test_returns_fallback_error(self):
        self.primary_mock_server.expect_request(
            uri="/openai/request",
        ).respond_with_data(
            response_data='{"some": "error"}',
            status=500,
        )

        self.fallback_mock_server.expect_request(
            uri="/openai/request",
            method="GET",
            headers={
                "Host": "localhost",
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "Content-Type": "application/json",
                "api-key": "fallback_dummy_api_key",
            },
            query_string={"key": "value"},
        ).respond_with_data(
            response_data='{"some": "fallback error"}',
            status=500,
        )

        response = requests.get(
            f"http://localhost:{self.app_server.port}/openai/request",
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "accept-encoding": "gzip",
                "api-key": "should be replaced",
                "host": "should be replaced",
            },
            params={"key": "value"},
        )

        self.assertEqual(response.content, b'{"some": "fallback error"}')
        self.assertEqual(response.status_code, 500)


if __name__ == "__main__":
    unittest.main()

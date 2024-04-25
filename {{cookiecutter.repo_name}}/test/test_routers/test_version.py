from test.resources import TestBase


class TestRoot(TestBase):
    def test_version(self):
        response = self.client.get("/version")
        self.assertEqual(200, response.status_code)
        self.assertEqual("some-fake-version", response.text)

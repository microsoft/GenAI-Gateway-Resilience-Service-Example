from test.resources import TestBase


class TestRoot(TestBase):
    def test_root(self):
        response = self.client.get("/")
        self.assertEqual(200, response.status_code)
        self.assertEqual("OK", response.text)

    def test_status(self):
        response = self.client.get("/status")
        self.assertEqual(200, response.status_code)
        self.assertEqual("OK", response.text)

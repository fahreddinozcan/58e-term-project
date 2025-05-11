import unittest
from app.app import app


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_hello(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Hello, security world!"})

    def test_health(self):
        response = self.app.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "healthy"})


if __name__ == "__main__":
    unittest.main()

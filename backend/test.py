import unittest
from backend import api

class TestFlaskAPI(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_valid_json(self):
        # Тест с корректным JSON
        response = self.app.post('/process', json={"key": "value"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("JSON received and parsed successfully", response.json['message'])
        self.assertEqual(response.json['data'], {"key": "value"})

    def test_invalid_json(self):
        # Тест с некорректным JSON
        response = self.app.post('/process', data="Not a JSON")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Request body must be JSON", response.json['error'])

    def test_empty_json(self):
        # Тест с пустым JSON
        response = self.app.post('/process', json={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['data'], {})

if __name__ == '__main__':
    unittest.main()
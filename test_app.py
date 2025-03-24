import unittest
from LostAndFound.app import app  # Import your Flask app

class BasicTests(unittest.TestCase):
    def setUp(self):
        """Set up the test client before each test"""
        self.app = app.test_client()
        self.app.testing = True

    def test_home(self):
        """Test the home page route"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login(self):
        """Test the login route"""
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()

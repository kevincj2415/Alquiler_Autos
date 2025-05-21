import unittest
from app import app

class BasicTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_main_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.app.get('/sesion')
        self.assertEqual(response.status_code, 200)

    def test_registro_page(self):
        response = self.app.get('/registro')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()

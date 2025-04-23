import unittest
from fastapi.testclient import TestClient
from fastapi import status
from main import app

class TestAPI(unittest.TestCase):
    """
    Тесты для проверки API приложения
    """
    
    def setUp(self):
        """
        Настройка перед каждым тестом
        """
        self.client = TestClient(app)
    
    def test_root_redirect(self):
        """
        Проверяет, что корневой маршрут перенаправляет на страницу логина
        """
        response = self.client.get("/", allow_redirects=False)
        self.assertEqual(response.status_code, status.HTTP_307_TEMPORARY_REDIRECT)
        self.assertEqual(response.headers["location"], "/login")
    
    def test_login_page(self):
        """
        Проверяет, что страница логина возвращает HTML
        """
        response = self.client.get("/login")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("text/html" in response.headers["content-type"])
    
    def test_register_page(self):
        """
        Проверяет, что страница регистрации возвращает HTML
        """
        response = self.client.get("/register")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("text/html" in response.headers["content-type"])
    
    def test_index_requires_auth(self):
        """
        Проверяет, что страница index требует авторизации
        """
        response = self.client.get("/index", allow_redirects=False)
        self.assertEqual(response.status_code, status.HTTP_303_SEE_OTHER)
        self.assertEqual(response.headers["location"], "/login")


if __name__ == "__main__":
    unittest.main() 
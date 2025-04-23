import unittest
from unittest.mock import MagicMock, patch
from db import crud
from db.models import User, Place, Recommendation

class TestRecommendations(unittest.TestCase):
    """
    Тесты для проверки функциональности рекомендаций
    """
    
    def setUp(self):
        """
        Настройка перед каждым тестом
        """
        # Создаем мок для сессии базы данных
        self.db = MagicMock()
        
        # Создаем тестовые данные
        self.test_user = User(id=1, username="testuser", hashed_password="hashedpassword")
        self.test_place = Place(
            id=1, 
            name="Тестовое место", 
            address="г. Вологда, ул. Тестовая, 123", 
            city="Вологда", 
            url="https://yandex.ru/maps", 
            rating=4.8
        )
    
    @patch('db.crud.get_recommendation')
    def test_add_recommendation_new(self, mock_get_recommendation):
        """
        Проверяет добавление новой рекомендации
        """
        # Настраиваем мок: рекомендация не существует
        mock_get_recommendation.return_value = None
        
        # Настраиваем мок для db.add()
        self.db.add = MagicMock()
        self.db.commit = MagicMock()
        self.db.refresh = MagicMock()
        
        # Вызываем тестируемую функцию
        result = crud.add_recommendation(self.db, user_id=1, place_id=1)
        
        # Проверяем, что функция get_recommendation была вызвана с правильными параметрами
        mock_get_recommendation.assert_called_once_with(self.db, 1, 1)
        
        # Проверяем, что db.add была вызвана
        self.db.add.assert_called_once()
        
        # Проверяем, что db.commit была вызвана
        self.db.commit.assert_called_once()
        
        # Проверяем, что db.refresh была вызвана
        self.db.refresh.assert_called_once()
    
    @patch('db.crud.get_recommendation')
    def test_add_recommendation_existing(self, mock_get_recommendation):
        """
        Проверяет добавление существующей рекомендации
        """
        # Создаем существующую рекомендацию
        existing_recommendation = Recommendation(user_id=1, place_id=1)
        
        # Настраиваем мок: рекомендация уже существует
        mock_get_recommendation.return_value = existing_recommendation
        
        # Настраиваем мок для db.add()
        self.db.add = MagicMock()
        
        # Вызываем тестируемую функцию
        result = crud.add_recommendation(self.db, user_id=1, place_id=1)
        
        # Проверяем, что функция get_recommendation была вызвана с правильными параметрами
        mock_get_recommendation.assert_called_once_with(self.db, 1, 1)
        
        # Проверяем, что db.add не была вызвана (так как рекомендация уже существует)
        self.db.add.assert_not_called()
        
        # Проверяем, что вернулась существующая рекомендация
        self.assertEqual(result, existing_recommendation)


if __name__ == "__main__":
    unittest.main() 
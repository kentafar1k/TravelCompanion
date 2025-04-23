import unittest
from services.yandex_parser import YandexMapsParser

class TestYandexMapsParser(unittest.TestCase):
    """
    Тесты для проверки функциональности YandexMapsParser
    """
    
    def setUp(self):
        """
        Настройка перед каждым тестом
        """
        self.parser = YandexMapsParser()
    
    def test_search_places_returns_one_result(self):
        """
        Проверяет, что метод search_places возвращает один результат
        """
        results = self.parser.search_places("кафе", "Вологда")
        
        # Проверяем, что вернулся список
        self.assertIsInstance(results, list)
        
        # Проверяем, что в списке ровно один элемент
        self.assertEqual(len(results), 1)
        
        # Проверяем структуру элемента
        result = results[0]
        self.assertIsInstance(result, dict)
        self.assertIn("id", result)
        self.assertIn("name", result)
        self.assertIn("address", result)
        self.assertIn("url", result)
        self.assertIn("rating", result)
        
        # Проверяем правильность значений
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["name"], "Результаты поиска 'кафе Вологда' на Яндекс.Картах")
        self.assertEqual(result["address"], "г. Вологда")
        self.assertTrue("yandex.ru/maps" in result["url"])
        self.assertTrue("кафе" in result["url"])
        self.assertTrue("Вологда" in result["url"])
        self.assertEqual(result["rating"], 5.0)
    
    def test_search_places_url_encoding(self):
        """
        Проверяет, что URL правильно кодируется
        """
        results = self.parser.search_places("кафе и рестораны", "Вологда")
        
        # Проверяем, что пробелы заменены на %20
        self.assertTrue("%20" in results[0]["url"])
        self.assertFalse(" " in results[0]["url"])


if __name__ == "__main__":
    unittest.main() 
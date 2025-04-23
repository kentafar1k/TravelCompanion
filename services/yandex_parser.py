from typing import List, Dict, Any

class YandexMapsParser:
    """
    Сервис для работы с Яндекс.Картами
    """
    
    def search_places(self, query: str, city: str, limit: int = 1) -> List[Dict[str, Any]]:
        """
        Создает прямую ссылку на поиск в Яндекс.Картах
        
        Args:
            query: Поисковый запрос
            city: Город для поиска
            limit: Максимальное количество результатов (игнорируется, всегда возвращается 1)
            
        Returns:
            List[Dict[str, Any]]: Список с одной ссылкой на поиск в Яндекс.Картах
        """
        # Формируем поисковый запрос для Яндекс.Карт
        search_query = f"{query} {city}"
        
        # Формируем ссылку на Яндекс.Карты с поисковым запросом
        url = f"https://yandex.ru/maps/?text={search_query.replace(' ', '%20')}"
        
        # Возвращаем один результат с прямой ссылкой
        return [{
            "id": 1,
            "name": f"Результаты поиска '{search_query}' на Яндекс.Картах",
            "address": f"г. {city}",
            "url": url,
            "rating": 5.0
        }] 
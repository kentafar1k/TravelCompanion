"""
Конфигурационный файл для pytest
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.database import Base, get_db
from main import app
from fastapi.testclient import TestClient
from db.models import User, Place, Recommendation
from core.security import get_password_hash

# Создаем тестовую базу данных SQLite в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Переопределяем зависимость get_db
@pytest.fixture
def override_get_db():
    # Создаем тестовую базу данных и таблицы
    Base.metadata.create_all(bind=engine)
    
    # Создаем тестовую сессию
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Удаляем все таблицы после тестов
        Base.metadata.drop_all(bind=engine)

# Фикстура для тестового клиента
@pytest.fixture
def client(override_get_db):
    # Переопределяем зависимость
    app.dependency_overrides[get_db] = lambda: override_get_db
    
    # Создаем тестовый клиент
    with TestClient(app) as test_client:
        yield test_client
    
    # Восстанавливаем оригинальную зависимость
    app.dependency_overrides = {}

# Фикстура для создания тестового пользователя
@pytest.fixture
def test_user(override_get_db):
    # Создаем тестового пользователя
    db = override_get_db
    hashed_password = get_password_hash("testpassword")
    user = User(username="testuser", hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Фикстура для создания тестового места
@pytest.fixture
def test_place(override_get_db):
    # Создаем тестовое место
    db = override_get_db
    place = Place(
        name="Тестовое место",
        address="г. Вологда, ул. Тестовая, 123",
        city="Вологда",
        url="https://yandex.ru/maps/?text=Тестовое%20место%20Вологда",
        rating=4.8
    )
    db.add(place)
    db.commit()
    db.refresh(place)
    return place 
# Логика работы с бд
from sqlalchemy.orm import Session
from . import models
from core.security import get_password_hash
from typing import List, Optional

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, username: str, password: str):
    hashed_password = get_password_hash(password)
    db_user = models.User(username=username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_admin_user(db: Session):
    # Проверяем существует ли уже пользователь admin
    admin = get_user(db, "admin")
    if not admin:
        # Создаем пользователя admin с паролем admin123
        admin = create_user(db, "admin", "admin123")
        return admin
    return admin

def get_place(db: Session, place_id: int):
    return db.query(models.Place).filter(models.Place.id == place_id).first()

def get_place_by_details(db: Session, name: str, address: str, city: str):
    return db.query(models.Place).filter(
        models.Place.name == name,
        models.Place.address == address,
        models.Place.city == city
    ).first()

def create_place(db: Session, name: str, address: str, city: str, url: str, rating: Optional[float] = None):
    db_place = models.Place(
        name=name,
        address=address,
        city=city,
        url=url,
        rating=rating
    )
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place

def get_or_create_place(db: Session, name: str, address: str, city: str, url: str, rating: Optional[float] = None):
    db_place = get_place_by_details(db, name, address, city)
    if db_place:
        return db_place
    return create_place(db, name, address, city, url, rating)

def get_user_recommendations(db: Session, user_id: int):
    return db.query(models.Recommendation).filter(models.Recommendation.user_id == user_id).all()

def get_recommendation(db: Session, user_id: int, place_id: int):
    return db.query(models.Recommendation).filter(
        models.Recommendation.user_id == user_id,
        models.Recommendation.place_id == place_id
    ).first()

def add_recommendation(db: Session, user_id: int, place_id: int):
    # Проверяем, существует ли уже рекомендация
    existing_recommendation = get_recommendation(db, user_id, place_id)
    if existing_recommendation:
        return existing_recommendation
    
    # Создаем новую рекомендацию
    db_recommendation = models.Recommendation(
        user_id=user_id,
        place_id=place_id
    )
    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation

def remove_recommendation(db: Session, user_id: int, place_id: int):
    db_recommendation = get_recommendation(db, user_id, place_id)
    if db_recommendation:
        db.delete(db_recommendation)
        db.commit()
        return True
    return False
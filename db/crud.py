# Логика работы с бд
from sqlalchemy.orm import Session
from . import models
from core.security import get_password_hash

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
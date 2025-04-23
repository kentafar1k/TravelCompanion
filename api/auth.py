from fastapi import APIRouter, HTTPException, Response, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db.database import get_db
from db import crud, models
from core.security import verify_password
from typing import Optional
import math

#login  keklik
#pwd    6823

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Роли пользователей (для админки)
ADMIN_USERS = {"admin"}  # Здесь можно добавить имена администраторов

@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        db_user = crud.get_user(db, username=username)
        if db_user:
            return templates.TemplateResponse(
                "register.html",
                {"request": request, "error": "Пользователь с таким именем уже существует"}
            )
        
        user = crud.create_user(db, username=username, password=password)
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "success": "Регистрация успешна! Теперь вы можете войти."}
        )
    except Exception as e:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Произошла ошибка при регистрации"}
        )

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    db_user = crud.get_user(db, username=username)
    if not db_user or not verify_password(password, db_user.hashed_password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Неверное имя пользователя или пароль"}
        )
    
    response = RedirectResponse(url="/index", status_code=303)
    response.set_cookie(
        key="session",
        value=username,
        httponly=True
    )
    return response

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="session")
    return response

@router.get("/index")
async def index(request: Request, db: Session = Depends(get_db)):
    username = request.cookies.get("session")
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    
    user = crud.get_user(db, username=username)
    if not user:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie(key="session")
        return response

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "username": username,
            "places": [],
            "search_query": "",
            "category": "entertainment"
        }
    )

@router.get("/admin")
async def admin_panel(
    request: Request, 
    page: int = 1, 
    db: Session = Depends(get_db)
):
    username = request.cookies.get("session")
    if not username or username not in ADMIN_USERS:
        return RedirectResponse(url="/login", status_code=303)
    
    # Получаем всех пользователей
    items_per_page = 10
    offset = (page - 1) * items_per_page
    
    # Запрос всех пользователей с пагинацией
    users = db.query(models.User).offset(offset).limit(items_per_page).all()
    
    # Подсчет общего количества пользователей для пагинации
    total_users = db.query(models.User).count()
    total_pages = math.ceil(total_users / items_per_page)
    
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "users": users,
            "current_page": page,
            "total_pages": total_pages
        }
    )

@router.get("/admin/users/edit/{user_id}")
async def edit_user_form(
    request: Request, 
    user_id: int, 
    db: Session = Depends(get_db)
):
    username = request.cookies.get("session")
    if not username or username not in ADMIN_USERS:
        return RedirectResponse(url="/login", status_code=303)
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return RedirectResponse(url="/admin", status_code=303)
    
    # Заглушка - здесь будет форма редактирования пользователя
    return {"message": "Форма редактирования пользователя будет здесь"}

@router.post("/admin/users/delete/{user_id}")
async def delete_user(
    request: Request, 
    user_id: int, 
    db: Session = Depends(get_db)
):
    username = request.cookies.get("session")
    if not username or username not in ADMIN_USERS:
        return RedirectResponse(url="/login", status_code=303)
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    
    return RedirectResponse(url="/admin", status_code=303)

@router.get("/search")
async def search(
    request: Request,
    query: str,
    category: str,
    db: Session = Depends(get_db)
):
    username = request.cookies.get("session")
    if not username:
        return RedirectResponse(url="/login", status_code=303)
    
    user = crud.get_user(db, username=username)
    if not user:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie(key="session")
        return response

    # Здесь будет логика поиска мест
    # Пока возвращаем тестовые данные
    places = [
        {
            "name": "Тестовое место",
            "address": "Тестовый адрес, 123",
            "category": "Развлечения" if category == "entertainment" else "Еда"
        }
    ] if query else []

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "username": username,
            "places": places,
            "search_query": query,
            "category": category
        }
    )

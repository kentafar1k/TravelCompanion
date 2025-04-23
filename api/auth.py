from fastapi import APIRouter, HTTPException, Response, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db.database import get_db
from db import crud, models
from core.security import verify_password
from typing import Optional, List, Dict
import math
from services.yandex_parser import YandexMapsParser

#login  admin
#pwd    admin123

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Роли пользователей (для админки)
ADMIN_USERS = {"admin"}  # Здесь можно добавить имена администраторов

# Инициализация парсера
yandex_parser = YandexMapsParser()

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

    # Получаем рекомендации пользователя
    user_recommendations = db.query(models.Recommendation).filter(
        models.Recommendation.user_id == user.id
    ).all()
    
    recommendations = []
    if user_recommendations:
        for rec in user_recommendations:
            place = db.query(models.Place).filter(models.Place.id == rec.place_id).first()
            if place:
                recommendations.append({
                    "id": place.id,
                    "name": place.name,
                    "address": place.address,
                    "category": place.category,
                    "url": place.url,
                    "rating": place.rating
                })

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "username": username,
            "places": [],
            "search_query": "",
            "category": "entertainment",
            "recommendations": recommendations
        }
    )

@router.get("/search")
async def search(
    request: Request,
    query: str,
    category: str,
    city: str = "Вологда",
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

    # Поиск мест через Яндекс.Карты (симуляция)
    found_places = yandex_parser.search_places(query, city, category)
    
    # Сохраняем найденные места в базу данных
    places = []
    for place_data in found_places:
        place = crud.get_or_create_place(
            db,
            name=place_data["name"],
            address=place_data["address"],
            city=city,
            category=place_data["category"],
            url=place_data["url"],
            rating=place_data["rating"]
        )
        places.append({
            "id": place.id,
            "name": place.name,
            "address": place.address,
            "category": place.category,
            "url": place.url,
            "rating": place.rating
        })
    
    # Получаем рекомендации пользователя
    user_recommendations = db.query(models.Recommendation).filter(
        models.Recommendation.user_id == user.id
    ).all()
    
    recommendations = []
    if user_recommendations:
        for rec in user_recommendations:
            place = db.query(models.Place).filter(models.Place.id == rec.place_id).first()
            if place:
                recommendations.append({
                    "id": place.id,
                    "name": place.name,
                    "address": place.address,
                    "category": place.category,
                    "url": place.url,
                    "rating": place.rating
                })

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "username": username,
            "places": places,
            "search_query": query,
            "category": category,
            "recommendations": recommendations
        }
    )

@router.post("/add_recommendation")
async def add_recommendation(
    request: Request,
    place_id: int = Form(...),
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
    
    # Добавляем рекомендацию
    place = crud.get_place(db, place_id)
    if not place:
        return RedirectResponse(url="/index", status_code=303)
    
    crud.add_recommendation(db, user.id, place.id)
    
    # Получаем параметры последнего поиска из реферера или формы
    referer = request.headers.get('referer', '')
    if 'search' in referer and 'query=' in referer:
        # Возвращаемся на страницу поиска с теми же параметрами
        return RedirectResponse(url=referer, status_code=303)
    else:
        # Если нет реферера, просто возвращаемся на главную
        return RedirectResponse(url="/index", status_code=303)

@router.post("/remove_recommendation")
async def remove_recommendation(
    request: Request,
    place_id: int = Form(...),
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
    
    # Удаляем рекомендацию
    crud.remove_recommendation(db, user.id, place_id)
    
    # Возвращаемся на главную страницу
    return RedirectResponse(url="/index", status_code=303)

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

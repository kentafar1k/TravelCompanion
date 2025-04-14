from fastapi import APIRouter, HTTPException, Response, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db.database import get_db
from db import crud, models
from core.security import verify_password
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")

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
    
    response = RedirectResponse(url="/index.html", status_code=303)
    response.set_cookie(
        key="session",
        value=username,
        httponly=True
    )
    return response

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login.html", status_code=303)
    response.delete_cookie(key="session")
    return response

@router.get("/index.html")
async def index(request: Request, db: Session = Depends(get_db)):
    username = request.cookies.get("session")
    if not username:
        return RedirectResponse(url="/login.html", status_code=303)
    
    user = crud.get_user(db, username=username)
    if not user:
        response = RedirectResponse(url="/login.html", status_code=303)
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

@router.get("/search")
async def search(
    request: Request,
    query: str,
    category: str,
    db: Session = Depends(get_db)
):
    username = request.cookies.get("session")
    if not username:
        return RedirectResponse(url="/login.html", status_code=303)
    
    user = crud.get_user(db, username=username)
    if not user:
        response = RedirectResponse(url="/login.html", status_code=303)
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

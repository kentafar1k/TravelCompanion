from fastapi import FastAPI, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from api.auth import router as auth_router
from db.database import engine, get_db
from db import models, crud
from sqlalchemy.orm import Session

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Create admin user on startup
@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    try:
        crud.create_admin_user(db)
    finally:
        db.close()

# Include authentication router
app.include_router(auth_router)

# Setup templates
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root():
    return RedirectResponse(url="/login")

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

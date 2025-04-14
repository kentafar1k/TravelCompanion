from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from api.auth import router as auth_router
from db.database import engine
from db import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include authentication router
app.include_router(auth_router)

# Mount templates directory last, so it doesn't override API routes
app.mount("/", StaticFiles(directory="templates", html=True), name="templates")

@app.get("/")
async def root():
    return RedirectResponse(url="/login.html")


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

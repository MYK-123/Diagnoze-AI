from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn
import sqlite3
import logging

from db.core import get_db, db_initialize
from .database import Database
from .auth_db import get_current_user
from .db_models import User, ChatHistory

from contextlib import asynccontextmanager

# Configure root logger so module loggers (diagnoze.*) are visible in the terminal
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger("diagnoze")
logger.setLevel(logging.DEBUG)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup
    db_initialize()
    yield
    # on shutdown
    pass

# Create FastAPI app
app = FastAPI(
    title="Diagnoze AI API",
    description="API for Diagnoze AI - Intelligent Symptom Analysis System",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware to log Authorization header for troubleshooting
@app.middleware("http")
async def log_auth_header(request: Request, call_next):
    auth_hdr = request.headers.get("authorization")
    logger.info("Incoming request %s %s Authorization=%s", request.method, request.url.path, auth_hdr)
    response = await call_next(request)
    return response

# Import routers AFTER creating app
from .routers import auth, users, chat, medical, admin

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(medical.router, prefix="/api/v1/medical", tags=["Medical"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Diagnoze AI API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/v1/system/health"
    }

# Database initialization endpoint
@app.get("/api/v1/system/init")
async def initialize_system():
    success = db_initialize()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "initialize_system_status": "success" if success else "failure",
        "service": "diagnoze-api",
        "version": "1.0.0"
    }

# Database reset endpoint
@app.get("/api/v1/system/reset")
async def reset_database():
    import db.core
    db.core.reset_database()
    db.core.populate_default_values()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "reset_system_status": "success",
        "service": "diagnoze-api",
        "version": "1.0.0"
    }


# Health check endpoint
@app.get("/api/v1/system/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "diagnoze-api",
        "version": "1.0.0"
    }

# System stats endpoint
@app.get("/api/v1/system/stats")
async def system_stats(conn: sqlite3.Connection = Depends(get_db)):
    db = Database(conn)
    total_users = db.fetch_scalar("SELECT COUNT(*) FROM users") or 0
    total_chats = db.fetch_scalar("SELECT COUNT(*) FROM chat_history") or 0
    total_diseases = db.fetch_scalar("SELECT COUNT(*) FROM disease") or 0
    total_symptoms = db.fetch_scalar("SELECT COUNT(*) FROM symptoms") or 0
    total_disease_symptoms = db.fetch_scalar("SELECT COUNT(*) FROM disease_symptoms") or 0
    total_educational_content = db.fetch_scalar("SELECT COUNT(*) FROM educational_content") or 0

    return {
        "total_users": total_users,
        "total_chats": total_chats,
        "total_diseases": total_diseases,
        "total_symptoms": total_symptoms,
        "total_disease_symptoms": total_disease_symptoms,
        "total_educational_content": total_educational_content,
        "uptime": "100%",
        "timestamp": datetime.now().isoformat()
    }

def run_api_server(host: str = "0.0.0.0", port: int = 9998):
    uvicorn.run(app, host=host, port=port, log_level="debug")

if __name__ == "__main__":
    run_api_server()




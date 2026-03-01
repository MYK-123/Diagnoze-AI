from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

from .database import init_db
from .database import get_db
from .auth_db import get_current_user
from .db_models import User, ChatHistory
from sqlalchemy import select
from sqlalchemy.orm import Session


from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup
    init_db()
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
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
async def system_stats(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return {
        "total_users": len(db.scalars(select(User.id)).all()),
        "total_chats": len(db.scalars(select(ChatHistory.id)).all()),
        "uptime": "100%",
        "timestamp": datetime.now().isoformat()
    }

def run_api_server(host: str = "0.0.0.0", port: int = 9998):
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_api_server()




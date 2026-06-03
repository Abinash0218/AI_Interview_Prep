from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.logging_config import setup_logging
from backend.database.connection import init_db
from backend.routers import auth_router, profile_router, chat_router, export_router

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AI Interview Preparation API",
    description="Backend API for AI-powered interview preparation",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(profile_router.router)
app.include_router(chat_router.router)
app.include_router(export_router.router)


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "AI Interview Preparation API"}

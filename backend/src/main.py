# backend/src/main.py
# from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.src.core.settings import get_settings
# from src.db.postgresql import engine

# Ensure Dramatiq tasks are discovered by importing them
from backend.src.api import router as api_router

"""
@asynccontextmanager
async def lifespan(app: FastAPI):
    # On Startup
    print("🚀 Starting Churninator API...")
    yield
    # On Shutdown
    print("🔌 Shutting down Churninator API...")
    await engine.dispose()
    print("Database connection pool closed.")"""


settings = get_settings()
app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG)  # , lifespan=lifespan)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Routers ---
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health"])
def read_root():
    return {"status": "ok", "project": settings.PROJECT_NAME}

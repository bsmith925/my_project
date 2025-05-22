"""Main FastAPI application module."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.routers import items
from app.routers import chat
from app.db import init_redis_models

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Tutor API",
    description="API for AI-powered tutoring conversations",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(items.router)
app.include_router(chat.router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Initializing services...")
    try:
        # Initialize Redis models
        await init_redis_models()
        logger.info("Redis models initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        # In production, you might want to exit the application if initialization fails
        # import sys
        # sys.exit(1)


@app.get("/")
async def root():
    """Root endpoint returning a welcome message."""
    return {"message": "Welcome to the AI Tutor API"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
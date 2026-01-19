"""
FastAPI Application Entry Point

This module initializes the FastAPI application and configures middleware,
routes, and error handlers for the DecisionTrace backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.logging_config import configure_logging, get_logger
from app.database import init_db, close_db

# Configure structlog
configure_logging()

# Get logger instance
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("application_starting", app_name=settings.APP_NAME)
    
    # Note: Database tables should be created via Alembic migrations
    # init_db() is available for development/testing but not called here
    # Uncomment the line below if you want to auto-create tables on startup
    # await init_db()
    
    logger.info("application_started", app_name=settings.APP_NAME)
    
    yield
    
    # Shutdown
    logger.info("application_shutting_down", app_name=settings.APP_NAME)
    await close_db()
    logger.info("application_shutdown_complete", app_name=settings.APP_NAME)


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered decision journal with structured analysis, bias detection, and outcome simulation",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Log application startup
logger.info(
    "application_startup",
    app_name=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    log_level=settings.LOG_LEVEL
)


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    logger.info("root_endpoint_accessed")
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    logger.debug("health_check_endpoint_accessed")
    return {
        "status": "healthy",
        "service": "decisiontrace-backend",
        "version": settings.APP_VERSION
    }


# Add API routes
from app.api.routes import decisions
app.include_router(decisions.router)

# Add error handling middleware
from app.middleware.error_handler import error_handler_middleware
app.middleware("http")(error_handler_middleware)

# Add logging middleware
from app.middleware.logging_middleware import logging_middleware
app.middleware("http")(logging_middleware)

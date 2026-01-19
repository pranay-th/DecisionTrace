"""
Error Handler Middleware

This middleware provides centralized error handling for the FastAPI application.
It catches exceptions and returns user-friendly error responses.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import structlog

from app.services.llm_client import GracefulFailureError

logger = structlog.get_logger(__name__)


async def error_handler_middleware(request: Request, call_next):
    """
    Middleware to handle errors and return user-friendly responses.
    
    This middleware catches:
    - GracefulFailureError: LLM/agent failures after retry and fallback
    - ValidationError: Pydantic validation failures
    - Exception: Any unexpected errors
    
    Args:
        request: FastAPI request object
        call_next: Next middleware/route handler
        
    Returns:
        Response from route handler or error response
    """
    try:
        # Call the next middleware/route handler
        response = await call_next(request)
        return response
        
    except GracefulFailureError as e:
        # LLM/agent failure after retry and fallback
        logger.error(
            "graceful_failure",
            path=request.url.path,
            method=request.method,
            error=str(e)
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": str(e),
                "message": "The operation could not be completed reliably. Please try again.",
                "type": "GracefulFailureError"
            }
        )
        
    except ValidationError as e:
        # Pydantic validation error
        logger.warning(
            "validation_error",
            path=request.url.path,
            method=request.method,
            errors=e.errors()
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation error",
                "message": "The provided data is invalid.",
                "details": e.errors(),
                "type": "ValidationError"
            }
        )
        
    except Exception as e:
        # Unexpected error
        logger.error(
            "unexpected_error",
            path=request.url.path,
            method=request.method,
            error=str(e),
            error_type=type(e).__name__
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred. Please try again later.",
                "type": type(e).__name__
            }
        )

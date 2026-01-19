"""
Logging Middleware

This middleware logs all incoming requests and outgoing responses.
"""

import time
from fastapi import Request
import structlog

logger = structlog.get_logger(__name__)


async def logging_middleware(request: Request, call_next):
    """
    Middleware to log all requests and responses.
    
    Logs:
    - Incoming request (method, path, client IP)
    - Outgoing response (status code, duration)
    
    Args:
        request: FastAPI request object
        call_next: Next middleware/route handler
        
    Returns:
        Response from route handler
    """
    # Record start time
    start_time = time.time()
    
    # Log incoming request
    logger.info(
        "request_started",
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else None
    )
    
    # Call the next middleware/route handler
    response = await call_next(request)
    
    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000
    
    # Log outgoing response
    logger.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms
    )
    
    return response

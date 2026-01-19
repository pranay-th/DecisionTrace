"""
Logging configuration and utilities for DecisionTrace.

This module provides a centralized logging configuration using structlog
and utility functions for consistent logging across the application.
"""

import structlog
from typing import Any, Dict

from app.config import settings


def configure_logging() -> None:
    """
    Configure structlog with appropriate processors and settings.
    
    This function should be called once at application startup.
    """
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    # Add appropriate renderer based on configuration
    if settings.LOG_FORMAT == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None) -> structlog.BoundLogger:
    """
    Get a logger instance with optional name binding.
    
    Args:
        name: Optional name to bind to the logger (e.g., module name)
        
    Returns:
        Configured structlog logger instance
    """
    logger = structlog.get_logger()
    if name:
        logger = logger.bind(logger_name=name)
    return logger


def log_agent_execution(
    logger: structlog.BoundLogger,
    agent_name: str,
    status: str,
    **kwargs: Any
) -> None:
    """
    Log agent execution with standardized format.
    
    Args:
        logger: Logger instance
        agent_name: Name of the agent being executed
        status: Execution status (started, success, failed)
        **kwargs: Additional context to log
    """
    logger.info(
        "agent_execution",
        agent_name=agent_name,
        status=status,
        **kwargs
    )


def log_llm_call(
    logger: structlog.BoundLogger,
    model: str,
    prompt_length: int,
    response_length: int = None,
    duration_ms: float = None,
    **kwargs: Any
) -> None:
    """
    Log LLM API call with standardized format.
    
    Args:
        logger: Logger instance
        model: Model name used
        prompt_length: Length of the prompt in characters
        response_length: Length of the response in characters (if available)
        duration_ms: Call duration in milliseconds (if available)
        **kwargs: Additional context to log
    """
    logger.info(
        "llm_call",
        model=model,
        prompt_length=prompt_length,
        response_length=response_length,
        duration_ms=duration_ms,
        **kwargs
    )


def log_validation_error(
    logger: structlog.BoundLogger,
    schema_name: str,
    error_details: Dict[str, Any],
    retry_count: int = 0,
    **kwargs: Any
) -> None:
    """
    Log validation error with standardized format.
    
    Args:
        logger: Logger instance
        schema_name: Name of the Pydantic schema that failed validation
        error_details: Validation error details
        retry_count: Current retry attempt number
        **kwargs: Additional context to log
    """
    logger.warning(
        "validation_error",
        schema_name=schema_name,
        error_details=error_details,
        retry_count=retry_count,
        **kwargs
    )

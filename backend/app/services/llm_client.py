"""
LLM Client for OpenRouter API integration.

This module provides the LLMClient class for interacting with OpenRouter's API,
including retry logic, model fallback, and structured output validation.
"""

import time
from enum import Enum
from typing import TypeVar, Type, Optional
import httpx
from pydantic import BaseModel, ValidationError
import structlog

from app.config import settings
from app.logging_config import log_llm_call, log_validation_error


# Type variable for generic Pydantic models
T = TypeVar('T', bound=BaseModel)


class ModelName(str, Enum):
    """Enum for supported LLM models."""
    PRIMARY = "deepseek/deepseek-chat"
    FALLBACK = "qwen/qwen-2.5-7b-instruct"


class GracefulFailureError(Exception):
    """
    Exception raised when all retry and fallback attempts fail.
    
    This exception indicates that the system could not complete the
    decision analysis reliably after exhausting all retry and fallback options.
    """
    pass


class LLMClient:
    """
    Client for interacting with OpenRouter API.
    
    This client handles:
    - API calls to OpenRouter
    - Structured output validation with Pydantic
    - Automatic retry on validation failure
    - Model fallback on retry failure
    - Comprehensive logging of all operations
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM client.
        
        Args:
            api_key: OpenRouter API key. If not provided, uses settings.OPENROUTER_API_KEY
        """
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.base_url = settings.OPENROUTER_BASE_URL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.timeout = settings.LLM_TIMEOUT
        self.logger = structlog.get_logger(__name__)
        self.current_model: Optional[str] = None
        
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
    
    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        model: ModelName = ModelName.PRIMARY,
        retry_count: int = 0
    ) -> T:
        """
        Generate structured output with validation, retry, and fallback.
        
        This method implements the following flow:
        1. Call the specified model with the prompt
        2. Validate the response against the Pydantic schema
        3. If validation fails and retry_count < max_retries, retry with same model
        4. If retry fails and using primary model, switch to fallback model
        5. If fallback fails, raise GracefulFailureError
        
        Args:
            prompt: The prompt to send to the LLM
            response_model: Pydantic model class for validation
            model: The model to use (PRIMARY or FALLBACK)
            retry_count: Current retry attempt (used internally)
            
        Returns:
            Validated instance of response_model
            
        Raises:
            GracefulFailureError: When all retry and fallback attempts fail
        """
        start_time = time.time()
        model_name = model.value
        self.current_model = model_name
        
        try:
            # Log the LLM call attempt
            self.logger.info(
                "llm_call_started",
                model=model_name,
                prompt_length=len(prompt),
                retry_count=retry_count
            )
            
            # Make API call to OpenRouter
            response_text = await self._call_openrouter(prompt, model)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Parse and validate response
            try:
                # Strip markdown code blocks if present (common LLM behavior)
                cleaned_response = self._clean_json_response(response_text)
                parsed = response_model.model_validate_json(cleaned_response)
                
                # Log successful call
                log_llm_call(
                    self.logger,
                    model=model_name,
                    prompt_length=len(prompt),
                    response_length=len(response_text),
                    duration_ms=duration_ms,
                    status="success",
                    retry_count=retry_count
                )
                
                return parsed
                
            except ValidationError as e:
                # Log validation error
                log_validation_error(
                    self.logger,
                    schema_name=response_model.__name__,
                    error_details=e.errors(),
                    retry_count=retry_count,
                    model=model_name
                )
                
                # Retry logic
                if retry_count < settings.MAX_RETRIES:
                    self.logger.info(
                        "retrying_with_same_model",
                        model=model_name,
                        retry_count=retry_count + 1
                    )
                    return await self.generate_structured(
                        prompt, response_model, model, retry_count + 1
                    )
                elif model == ModelName.PRIMARY and settings.ENABLE_FALLBACK:
                    # Switch to fallback model
                    self.logger.warning(
                        "fallback_triggered",
                        from_model=model_name,
                        to_model=ModelName.FALLBACK.value,
                        reason="validation_failure_after_retry"
                    )
                    return await self.generate_structured(
                        prompt, response_model, ModelName.FALLBACK, retry_count=0
                    )
                else:
                    # All attempts failed
                    self.logger.error(
                        "all_attempts_failed",
                        model=model_name,
                        retry_count=retry_count,
                        schema_name=response_model.__name__
                    )
                    raise GracefulFailureError(
                        "Decision analysis could not be completed reliably. "
                        "All models failed validation."
                    )
                    
        except httpx.TimeoutException as e:
            self.logger.error(
                "llm_call_timeout",
                model=model_name,
                timeout=self.timeout,
                retry_count=retry_count
            )
            raise GracefulFailureError(
                f"Decision analysis timed out after {self.timeout} seconds."
            )
            
        except httpx.HTTPStatusError as e:
            self.logger.error(
                "llm_call_http_error",
                model=model_name,
                status_code=e.response.status_code,
                error=str(e),
                retry_count=retry_count
            )
            raise GracefulFailureError(
                f"LLM API error: {e.response.status_code}"
            )
            
        except Exception as e:
            self.logger.error(
                "llm_call_unexpected_error",
                model=model_name,
                error=str(e),
                error_type=type(e).__name__,
                retry_count=retry_count
            )
            # Don't wrap GracefulFailureError - just re-raise it
            if isinstance(e, GracefulFailureError):
                raise
            raise GracefulFailureError(
                f"Unexpected error during decision analysis: {str(e)}"
            )
    
    async def _call_openrouter(self, prompt: str, model: ModelName) -> str:
        """
        Make an API call to OpenRouter.
        
        Args:
            prompt: The prompt to send
            model: The model to use
            
        Returns:
            The response text from the API
            
        Raises:
            httpx.TimeoutException: If the request times out
            httpx.HTTPStatusError: If the API returns an error status
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://decisiontrace.app",  # Optional but recommended
                    "X-Title": "DecisionTrace"  # Optional but recommended
                },
                json={
                    "model": model.value,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens
                },
                timeout=self.timeout
            )
            
            # Raise exception for error status codes
            response.raise_for_status()
            
            # Extract the response content
            response_data = response.json()
            return response_data["choices"][0]["message"]["content"]
    
    def _clean_json_response(self, response: str) -> str:
        """
        Clean JSON response by removing markdown code blocks.
        
        Many LLMs wrap JSON in markdown code blocks like:
        ```json
        {"key": "value"}
        ```
        
        This method strips those markers to get clean JSON.
        
        Args:
            response: Raw response text from LLM
            
        Returns:
            Cleaned JSON string
        """
        response = response.strip()
        
        # Remove markdown code blocks
        if response.startswith("```"):
            # Find the first newline after ```
            first_newline = response.find("\n")
            if first_newline != -1:
                response = response[first_newline + 1:]
            
            # Remove trailing ```
            if response.endswith("```"):
                response = response[:-3]
        
        return response.strip()

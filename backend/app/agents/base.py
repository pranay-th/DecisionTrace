"""
Base Agent Framework

This module provides the abstract BaseAgent class that all agents must extend.
It handles LLM client integration, prompt building, and execution logging.
"""

from abc import ABC, abstractmethod
from typing import Type, Dict, Any
from datetime import datetime
import structlog
from pydantic import BaseModel

from app.services.llm_client import LLMClient, GracefulFailureError
from app.logging_config import log_agent_execution


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the DecisionTrace pipeline.
    
    All agents must implement:
    - get_system_prompt(): Return the system prompt for this agent
    - get_response_model(): Return the Pydantic model for validation
    - _format_input(): Format input data for the prompt
    
    The execute() method is provided and handles:
    - Prompt building
    - LLM client integration
    - Response validation
    - Execution logging
    """
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize the agent with an LLM client.
        
        Args:
            llm_client: LLMClient instance for making API calls
        """
        self.llm_client = llm_client
        self.logger = structlog.get_logger(self.__class__.__name__)
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Return the system prompt for this agent.
        
        This prompt defines the agent's role, instructions, and output format.
        
        Returns:
            System prompt string
        """
        pass
    
    @abstractmethod
    def get_response_model(self) -> Type[BaseModel]:
        """
        Return the Pydantic model for validation.
        
        This model defines the expected structure of the agent's output.
        
        Returns:
            Pydantic model class
        """
        pass
    
    @abstractmethod
    def _format_input(self, input_data: Dict[str, Any]) -> str:
        """
        Format input data for the prompt.
        
        This method transforms the input dictionary into a formatted string
        that will be appended to the system prompt.
        
        Args:
            input_data: Dictionary containing input data for the agent
            
        Returns:
            Formatted input string
        """
        pass
    
    async def execute(self, input_data: Dict[str, Any]) -> BaseModel:
        """
        Execute the agent with input data.
        
        This method:
        1. Logs execution start
        2. Builds the full prompt
        3. Calls the LLM client
        4. Validates the response
        5. Logs execution end
        6. Returns the validated result
        
        Args:
            input_data: Dictionary containing input data for the agent
            
        Returns:
            Validated Pydantic model instance
            
        Raises:
            GracefulFailureError: If the agent execution fails
        """
        agent_name = self.__class__.__name__
        start_time = datetime.utcnow()
        
        # Log execution start
        log_agent_execution(
            self.logger,
            agent_name=agent_name,
            status="started",
            input_data_keys=list(input_data.keys()),
            timestamp=start_time.isoformat()
        )
        
        try:
            # Build the full prompt
            prompt = self._build_prompt(input_data)
            
            # Call LLM client with structured output
            result = await self.llm_client.generate_structured(
                prompt=prompt,
                response_model=self.get_response_model()
            )
            
            # Log execution success
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            log_agent_execution(
                self.logger,
                agent_name=agent_name,
                status="success",
                duration_ms=duration_ms,
                model_used=self.llm_client.current_model,
                timestamp=end_time.isoformat()
            )
            
            return result
            
        except GracefulFailureError as e:
            # Log execution failure
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            log_agent_execution(
                self.logger,
                agent_name=agent_name,
                status="failed",
                error=str(e),
                duration_ms=duration_ms,
                timestamp=end_time.isoformat()
            )
            
            # Re-raise the error
            raise
            
        except Exception as e:
            # Log unexpected error
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            log_agent_execution(
                self.logger,
                agent_name=agent_name,
                status="failed",
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=duration_ms,
                timestamp=end_time.isoformat()
            )
            
            # Wrap in GracefulFailureError
            raise GracefulFailureError(
                f"{agent_name} failed: {str(e)}"
            )
    
    def _build_prompt(self, input_data: Dict[str, Any]) -> str:
        """
        Build the full prompt from system prompt and input data.
        
        Args:
            input_data: Dictionary containing input data
            
        Returns:
            Complete prompt string
        """
        system_prompt = self.get_system_prompt()
        user_input = self._format_input(input_data)
        
        return f"{system_prompt}\n\n{user_input}"

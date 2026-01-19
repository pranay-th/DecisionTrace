"""
DecisionOrchestrator - Pipeline orchestrator for agent execution.

This module provides the DecisionOrchestrator class that chains all agents together,
handles errors with retry and fallback logic, and persists results to the database.
"""

from datetime import datetime
from typing import Dict, Any, List
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import BaseAgent
from app.agents.decision_structuring import DecisionStructuringAgent
from app.agents.bias_detection import BiasDetectionAgent
from app.agents.outcome_simulation import OutcomeSimulationAgent
from app.agents.reflection import ReflectionAgent
from app.services.llm_client import LLMClient, GracefulFailureError
from app.schemas.decision_input import DecisionInput
from app.models.decision import Decision


class DecisionOrchestrator:
    """
    Orchestrator for the DecisionTrace agent pipeline.
    
    This class:
    - Initializes all agents with a shared LLM client
    - Executes agents in strict sequential order
    - Validates outputs at each stage
    - Handles errors with retry and fallback logic
    - Logs all execution details
    - Persists results to the database
    
    The pipeline flow:
    1. DecisionStructuringAgent - Structures raw input
    2. BiasDetectionAgent - Detects cognitive biases
    3. OutcomeSimulationAgent - Simulates future scenarios
    4. ReflectionAgent - (Deferred, only when actual outcome is provided)
    """
    
    def __init__(
        self,
        llm_client: LLMClient,
        db_session: AsyncSession
    ):
        """
        Initialize the orchestrator with LLM client and database session.
        
        Args:
            llm_client: LLMClient instance for making API calls
            db_session: AsyncSession for database operations
        """
        self.llm_client = llm_client
        self.db_session = db_session
        self.logger = structlog.get_logger(__name__)
        
        # Initialize all agents with shared LLM client
        self.structuring_agent = DecisionStructuringAgent(llm_client)
        self.bias_agent = BiasDetectionAgent(llm_client)
        self.outcome_agent = OutcomeSimulationAgent(llm_client)
        self.reflection_agent = ReflectionAgent(llm_client)
        
        self.logger.info(
            "orchestrator_initialized",
            agents=["DecisionStructuringAgent", "BiasDetectionAgent", 
                   "OutcomeSimulationAgent", "ReflectionAgent"]
        )
    
    async def process_decision(
        self,
        decision_input: DecisionInput
    ) -> Decision:
        """
        Execute the full agent pipeline with validation and error handling.
        
        This method:
        1. Executes DecisionStructuringAgent
        2. Executes BiasDetectionAgent with structured decision
        3. Executes OutcomeSimulationAgent with structured decision and bias report
        4. Saves all results to database
        5. Returns the persisted Decision object
        
        Args:
            decision_input: Validated user input
            
        Returns:
            Decision object with all agent outputs
            
        Raises:
            GracefulFailureError: If any agent fails after retry and fallback
        """
        execution_log: List[Dict[str, Any]] = []
        pipeline_start_time = datetime.utcnow()
        
        self.logger.info(
            "pipeline_started",
            title=decision_input.title,
            timestamp=pipeline_start_time.isoformat()
        )
        
        try:
            # Step 1: Structure the decision
            self.logger.info("pipeline_step", step=1, agent="DecisionStructuringAgent")
            structured = await self._execute_with_logging(
                self.structuring_agent,
                {"input": decision_input.model_dump()},
                "DecisionStructuringAgent",
                execution_log
            )
            
            # Step 2: Detect biases
            self.logger.info("pipeline_step", step=2, agent="BiasDetectionAgent")
            bias_report = await self._execute_with_logging(
                self.bias_agent,
                {"structured_decision": structured.model_dump()},
                "BiasDetectionAgent",
                execution_log
            )
            
            # Step 3: Simulate outcomes
            self.logger.info("pipeline_step", step=3, agent="OutcomeSimulationAgent")
            outcomes = await self._execute_with_logging(
                self.outcome_agent,
                {
                    "structured_decision": structured.model_dump(),
                    "bias_report": bias_report.model_dump()
                },
                "OutcomeSimulationAgent",
                execution_log
            )
            
            # Pipeline completed successfully
            pipeline_end_time = datetime.utcnow()
            pipeline_duration_ms = (pipeline_end_time - pipeline_start_time).total_seconds() * 1000
            
            self.logger.info(
                "pipeline_completed",
                duration_ms=pipeline_duration_ms,
                timestamp=pipeline_end_time.isoformat()
            )
            
            # Save to database
            decision = await self._save_decision(
                decision_input=decision_input,
                structured_decision=structured.model_dump(),
                bias_report=bias_report.model_dump(),
                outcome_simulations=outcomes.model_dump(),
                execution_log=execution_log
            )
            
            return decision
            
        except GracefulFailureError as e:
            # Log pipeline failure
            pipeline_end_time = datetime.utcnow()
            pipeline_duration_ms = (pipeline_end_time - pipeline_start_time).total_seconds() * 1000
            
            execution_log.append({
                "event": "pipeline_failed",
                "error": str(e),
                "timestamp": pipeline_end_time.isoformat(),
                "duration_ms": pipeline_duration_ms
            })
            
            self.logger.error(
                "pipeline_failed",
                error=str(e),
                duration_ms=pipeline_duration_ms,
                timestamp=pipeline_end_time.isoformat()
            )
            
            # Re-raise the error to be handled by API layer
            raise
            
        except Exception as e:
            # Log unexpected error
            pipeline_end_time = datetime.utcnow()
            pipeline_duration_ms = (pipeline_end_time - pipeline_start_time).total_seconds() * 1000
            
            execution_log.append({
                "event": "pipeline_error",
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": pipeline_end_time.isoformat(),
                "duration_ms": pipeline_duration_ms
            })
            
            self.logger.error(
                "pipeline_unexpected_error",
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=pipeline_duration_ms,
                timestamp=pipeline_end_time.isoformat()
            )
            
            # Wrap in GracefulFailureError
            raise GracefulFailureError(
                f"Decision analysis failed unexpectedly: {str(e)}"
            )
    
    async def _execute_with_logging(
        self,
        agent: BaseAgent,
        input_data: Dict[str, Any],
        agent_name: str,
        execution_log: List[Dict[str, Any]]
    ) -> Any:
        """
        Execute agent and log execution details.
        
        This helper method:
        - Records execution start time
        - Executes the agent
        - Records execution end time and duration
        - Logs success or failure
        - Appends execution details to execution_log
        
        Args:
            agent: Agent instance to execute
            input_data: Input data for the agent
            agent_name: Name of the agent (for logging)
            execution_log: List to append execution details to
            
        Returns:
            Agent output (validated Pydantic model)
            
        Raises:
            GracefulFailureError: If agent execution fails
        """
        start_time = datetime.utcnow()
        
        try:
            # Execute the agent
            result = await agent.execute(input_data)
            
            # Record success
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            execution_log.append({
                "agent": agent_name,
                "status": "success",
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_ms": duration_ms,
                "model_used": self.llm_client.current_model
            })
            
            self.logger.info(
                "agent_execution_success",
                agent=agent_name,
                duration_ms=duration_ms,
                model_used=self.llm_client.current_model
            )
            
            return result
            
        except GracefulFailureError as e:
            # Record failure
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            execution_log.append({
                "agent": agent_name,
                "status": "failed",
                "error": str(e),
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_ms": duration_ms
            })
            
            self.logger.error(
                "agent_execution_failed",
                agent=agent_name,
                error=str(e),
                duration_ms=duration_ms
            )
            
            # Re-raise the error
            raise
            
        except Exception as e:
            # Record unexpected error
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            
            execution_log.append({
                "agent": agent_name,
                "status": "failed",
                "error": str(e),
                "error_type": type(e).__name__,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_ms": duration_ms
            })
            
            self.logger.error(
                "agent_execution_unexpected_error",
                agent=agent_name,
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=duration_ms
            )
            
            # Wrap in GracefulFailureError
            raise GracefulFailureError(
                f"{agent_name} failed: {str(e)}"
            )
    
    async def _save_decision(
        self,
        decision_input: DecisionInput,
        structured_decision: Dict[str, Any],
        bias_report: Dict[str, Any],
        outcome_simulations: Dict[str, Any],
        execution_log: List[Dict[str, Any]]
    ) -> Decision:
        """
        Save decision with all agent outputs to the database.
        
        This method:
        - Creates a Decision model instance
        - Populates all fields
        - Adds to database session
        - Commits the transaction
        - Handles database errors gracefully
        
        Args:
            decision_input: Original user input
            structured_decision: Output from DecisionStructuringAgent
            bias_report: Output from BiasDetectionAgent
            outcome_simulations: Output from OutcomeSimulationAgent
            execution_log: List of execution details
            
        Returns:
            Persisted Decision object
            
        Raises:
            GracefulFailureError: If database operation fails
        """
        try:
            # Create Decision model instance
            decision = Decision(
                title=decision_input.title,
                context=decision_input.context,
                constraints=decision_input.constraints,
                options=decision_input.options,
                structured_decision=structured_decision,
                bias_report=bias_report,
                outcome_simulations=outcome_simulations,
                execution_log=execution_log
            )
            
            # Add to session
            self.db_session.add(decision)
            
            # Commit transaction
            await self.db_session.commit()
            
            # Refresh to get generated fields (id, timestamps)
            await self.db_session.refresh(decision)
            
            self.logger.info(
                "decision_saved",
                decision_id=str(decision.id),
                title=decision.title
            )
            
            return decision
            
        except Exception as e:
            # Rollback transaction
            await self.db_session.rollback()
            
            self.logger.error(
                "database_save_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            
            # Wrap in GracefulFailureError
            raise GracefulFailureError(
                f"Failed to save decision to database: {str(e)}"
            )
    
    async def add_reflection(
        self,
        decision_id: str,
        actual_outcome: str
    ) -> Decision:
        """
        Add reflection to an existing decision.
        
        This method:
        1. Fetches the existing decision from database
        2. Executes ReflectionAgent with original decision and actual outcome
        3. Updates decision with reflection insight
        4. Saves updated decision to database
        
        Args:
            decision_id: UUID of the decision
            actual_outcome: User-provided actual outcome
            
        Returns:
            Updated Decision object with reflection insight
            
        Raises:
            GracefulFailureError: If reflection fails or decision not found
        """
        execution_log: List[Dict[str, Any]] = []
        
        try:
            # Fetch existing decision
            from sqlalchemy import select
            from uuid import UUID
            
            result = await self.db_session.execute(
                select(Decision).where(Decision.id == UUID(decision_id))
            )
            decision = result.scalar_one_or_none()
            
            if not decision:
                raise GracefulFailureError(f"Decision {decision_id} not found")
            
            self.logger.info(
                "reflection_started",
                decision_id=decision_id
            )
            
            # Execute ReflectionAgent
            reflection_insight = await self._execute_with_logging(
                self.reflection_agent,
                {
                    "decision": {
                        "title": decision.title,
                        "context": decision.context,
                        "structured_decision": decision.structured_decision,
                        "bias_report": decision.bias_report
                    },
                    "outcome_simulations": decision.outcome_simulations,
                    "actual_outcome": actual_outcome
                },
                "ReflectionAgent",
                execution_log
            )
            
            # Update decision
            decision.reflection_insight = reflection_insight.model_dump()
            decision.actual_outcome = actual_outcome
            decision.actual_outcome_date = datetime.utcnow()
            
            # Append reflection execution to existing log
            if decision.execution_log:
                decision.execution_log.extend(execution_log)
            else:
                decision.execution_log = execution_log
            
            # Commit changes
            await self.db_session.commit()
            await self.db_session.refresh(decision)
            
            self.logger.info(
                "reflection_completed",
                decision_id=decision_id
            )
            
            return decision
            
        except GracefulFailureError:
            # Re-raise GracefulFailureError
            raise
            
        except Exception as e:
            # Rollback transaction
            await self.db_session.rollback()
            
            self.logger.error(
                "reflection_failed",
                decision_id=decision_id,
                error=str(e),
                error_type=type(e).__name__
            )
            
            # Wrap in GracefulFailureError
            raise GracefulFailureError(
                f"Failed to add reflection: {str(e)}"
            )

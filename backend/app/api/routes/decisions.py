"""
Decision API Routes

This module provides REST API endpoints for decision management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List

from app.agents.orchestrator import DecisionOrchestrator
from app.services.llm_client import LLMClient, GracefulFailureError
from app.schemas.decision_input import DecisionInput
from app.schemas.reflection_input import ReflectionInput
from app.models.decision import Decision
from app.database import get_db
from app.config import settings
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/decisions", tags=["decisions"])


def get_llm_client() -> LLMClient:
    """Dependency to get LLM client instance."""
    return LLMClient(api_key=settings.OPENROUTER_API_KEY)


def get_orchestrator(
    llm_client: LLMClient = Depends(get_llm_client),
    db: AsyncSession = Depends(get_db)
) -> DecisionOrchestrator:
    """Dependency to get orchestrator instance."""
    return DecisionOrchestrator(llm_client=llm_client, db_session=db)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_decision(
    decision_input: DecisionInput,
    orchestrator: DecisionOrchestrator = Depends(get_orchestrator)
):
    """
    Create and analyze a new decision.
    
    This endpoint:
    1. Validates input with DecisionInput schema (automatic)
    2. Executes the agent pipeline (structuring, bias detection, outcome simulation)
    3. Persists decision with all agent outputs to database
    4. Returns the complete decision with all analysis
    
    Args:
        decision_input: User input for the decision
        orchestrator: Orchestrator instance (dependency injection)
        
    Returns:
        Decision object with all agent outputs:
        - id, created_at, updated_at
        - title, context, constraints, options (user input)
        - structured_decision (from DecisionStructuringAgent)
        - bias_report (from BiasDetectionAgent)
        - outcome_simulations (from OutcomeSimulationAgent)
        - execution_log (pipeline execution details)
        
    Raises:
        HTTPException 422: If input validation fails
        HTTPException 500: If analysis fails after retry and fallback
    """
    logger.info(
        "create_decision_request",
        title=decision_input.title
    )
    
    try:
        # Process decision through agent pipeline
        decision = await orchestrator.process_decision(decision_input)
        
        logger.info(
            "create_decision_success",
            decision_id=str(decision.id),
            title=decision.title
        )
        
        # Return decision as dict
        return decision.to_dict()
        
    except GracefulFailureError as e:
        # Log and return user-friendly error
        logger.error(
            "create_decision_failed",
            error=str(e),
            title=decision_input.title
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": str(e),
                "message": "Decision analysis could not be completed reliably. Please try again."
            }
        )
        
    except Exception as e:
        # Log unexpected error
        logger.error(
            "create_decision_unexpected_error",
            error=str(e),
            error_type=type(e).__name__,
            title=decision_input.title
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred during decision analysis."
            }
        )


@router.get("/", status_code=status.HTTP_200_OK)
async def list_decisions(
    db: AsyncSession = Depends(get_db)
):
    """
    List all decisions.
    
    Returns a list of all decisions with basic information:
    - id, title, created_at
    - has_reflection (boolean indicating if reflection exists)
    
    Decisions are ordered by created_at descending (most recent first).
    
    Args:
        db: Database session (dependency injection)
        
    Returns:
        List of decision summaries
    """
    logger.info("list_decisions_request")
    
    try:
        # Query all decisions, ordered by created_at descending
        result = await db.execute(
            select(Decision).order_by(Decision.created_at.desc())
        )
        decisions = result.scalars().all()
        
        # Return list of decision summaries
        decision_list = [
            {
                "id": str(d.id),
                "title": d.title,
                "created_at": d.created_at.isoformat(),
                "has_reflection": d.has_reflection
            }
            for d in decisions
        ]
        
        logger.info(
            "list_decisions_success",
            count=len(decision_list)
        )
        
        return {"decisions": decision_list}
        
    except Exception as e:
        logger.error(
            "list_decisions_failed",
            error=str(e),
            error_type=type(e).__name__
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "Failed to retrieve decisions."
            }
        )


@router.get("/{decision_id}", status_code=status.HTTP_200_OK)
async def get_decision(
    decision_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get decision details by ID.
    
    Returns the complete decision with all agent outputs:
    - User input (title, context, constraints, options)
    - Structured decision
    - Bias report
    - Outcome simulations
    - Reflection insight (if available)
    - Execution log
    
    Args:
        decision_id: UUID of the decision
        db: Database session (dependency injection)
        
    Returns:
        Complete decision object
        
    Raises:
        HTTPException 404: If decision not found
        HTTPException 400: If decision_id is invalid UUID
    """
    logger.info(
        "get_decision_request",
        decision_id=decision_id
    )
    
    try:
        # Parse UUID
        try:
            decision_uuid = UUID(decision_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Invalid decision ID",
                    "message": f"'{decision_id}' is not a valid UUID."
                }
            )
        
        # Query decision by ID
        result = await db.execute(
            select(Decision).where(Decision.id == decision_uuid)
        )
        decision = result.scalar_one_or_none()
        
        if not decision:
            logger.warning(
                "get_decision_not_found",
                decision_id=decision_id
            )
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "Decision not found",
                    "message": f"Decision with ID '{decision_id}' does not exist."
                }
            )
        
        logger.info(
            "get_decision_success",
            decision_id=decision_id,
            title=decision.title
        )
        
        # Return full decision
        return decision.to_dict()
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(
            "get_decision_failed",
            decision_id=decision_id,
            error=str(e),
            error_type=type(e).__name__
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "Failed to retrieve decision."
            }
        )


@router.post("/{decision_id}/reflect", status_code=status.HTTP_200_OK)
async def add_reflection(
    decision_id: str,
    reflection_input: ReflectionInput,
    orchestrator: DecisionOrchestrator = Depends(get_orchestrator)
):
    """
    Add reflection to an existing decision.
    
    This endpoint:
    1. Fetches the existing decision from database
    2. Executes ReflectionAgent with original decision and actual outcome
    3. Updates decision with reflection insight
    4. Returns updated decision
    
    Args:
        decision_id: UUID of the decision
        reflection_input: ReflectionInput schema containing actual_outcome
        orchestrator: Orchestrator instance (dependency injection)
        
    Returns:
        Updated decision with reflection insight:
        - accuracy_score (0.0 to 1.0)
        - lessons_learned (list of lessons)
        - repeated_patterns (list of patterns)
        
    Raises:
        HTTPException 404: If decision not found
        HTTPException 400: If decision_id is invalid UUID
        HTTPException 422: If reflection_input validation fails
        HTTPException 500: If reflection fails
    """
    logger.info(
        "add_reflection_request",
        decision_id=decision_id
    )
    
    try:
        # Add reflection via orchestrator
        decision = await orchestrator.add_reflection(
            decision_id=decision_id,
            actual_outcome=reflection_input.actual_outcome
        )
        
        logger.info(
            "add_reflection_success",
            decision_id=decision_id,
            accuracy_score=decision.reflection_insight.get('accuracy_score')
        )
        
        # Return updated decision
        return decision.to_dict()
        
    except GracefulFailureError as e:
        # Check if it's a "not found" error
        if "not found" in str(e).lower():
            logger.warning(
                "add_reflection_not_found",
                decision_id=decision_id
            )
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": str(e),
                    "message": f"Decision with ID '{decision_id}' does not exist."
                }
            )
        else:
            # Other graceful failure
            logger.error(
                "add_reflection_failed",
                decision_id=decision_id,
                error=str(e)
            )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": str(e),
                    "message": "Reflection could not be completed reliably. Please try again."
                }
            )
            
    except Exception as e:
        logger.error(
            "add_reflection_unexpected_error",
            decision_id=decision_id,
            error=str(e),
            error_type=type(e).__name__
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred during reflection."
            }
        )

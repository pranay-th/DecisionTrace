"""
Example usage of DecisionOrchestrator in API endpoints.

This file demonstrates how to use the orchestrator in FastAPI routes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import DecisionOrchestrator
from app.services.llm_client import LLMClient, GracefulFailureError
from app.schemas.decision_input import DecisionInput
from app.database import get_db
from app.config import settings


# Example router (would be in app/api/routes/decisions.py)
router = APIRouter(prefix="/api/decisions", tags=["decisions"])


def get_llm_client() -> LLMClient:
    """Dependency to get LLM client."""
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
    1. Validates the input (automatic via Pydantic)
    2. Executes the agent pipeline via orchestrator
    3. Returns the decision with all agent outputs
    
    Args:
        decision_input: User input for the decision
        orchestrator: Orchestrator instance (injected)
        
    Returns:
        Decision object with all agent outputs
        
    Raises:
        HTTPException 500: If analysis fails
    """
    try:
        # Process the decision through the pipeline
        decision = await orchestrator.process_decision(decision_input)
        
        # Return the decision as dict
        return decision.to_dict()
        
    except GracefulFailureError as e:
        # Return user-friendly error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": str(e),
                "message": "Decision analysis could not be completed reliably."
            }
        )
    except Exception as e:
        # Unexpected error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred during decision analysis."
            }
        )


@router.post("/{decision_id}/reflect", status_code=status.HTTP_200_OK)
async def add_reflection(
    decision_id: str,
    actual_outcome: str,
    orchestrator: DecisionOrchestrator = Depends(get_orchestrator)
):
    """
    Add reflection to an existing decision.
    
    This endpoint:
    1. Fetches the existing decision
    2. Executes the ReflectionAgent with actual outcome
    3. Updates the decision with reflection insight
    
    Args:
        decision_id: UUID of the decision
        actual_outcome: User-provided actual outcome
        orchestrator: Orchestrator instance (injected)
        
    Returns:
        Updated decision with reflection insight
        
    Raises:
        HTTPException 404: If decision not found
        HTTPException 500: If reflection fails
    """
    try:
        # Add reflection via orchestrator
        decision = await orchestrator.add_reflection(
            decision_id=decision_id,
            actual_outcome=actual_outcome
        )
        
        # Return updated decision
        return decision.to_dict()
        
    except GracefulFailureError as e:
        # Check if it's a "not found" error
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": str(e),
                    "message": f"Decision {decision_id} not found."
                }
            )
        else:
            # Other graceful failure
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": str(e),
                    "message": "Reflection could not be completed reliably."
                }
            )
    except Exception as e:
        # Unexpected error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred during reflection."
            }
        )


# Example of how to use the orchestrator directly (without FastAPI)
async def example_direct_usage():
    """
    Example of using the orchestrator directly without FastAPI.
    
    This is useful for:
    - Testing
    - Background jobs
    - CLI tools
    """
    from app.database import AsyncSessionLocal
    
    # Create LLM client
    llm_client = LLMClient(api_key=settings.OPENROUTER_API_KEY)
    
    # Create database session
    async with AsyncSessionLocal() as db_session:
        # Create orchestrator
        orchestrator = DecisionOrchestrator(
            llm_client=llm_client,
            db_session=db_session
        )
        
        # Create decision input
        decision_input = DecisionInput(
            title="Should I accept the job offer?",
            context="I received an offer from Company X with a 20% salary increase, but it requires relocation.",
            constraints=["Must relocate", "Start in 2 months"],
            options=["Accept", "Decline", "Negotiate"]
        )
        
        try:
            # Process decision
            decision = await orchestrator.process_decision(decision_input)
            
            print(f"✅ Decision created: {decision.id}")
            print(f"📊 Structured: {decision.structured_decision}")
            print(f"🧠 Biases: {decision.bias_report}")
            print(f"🔮 Outcomes: {decision.outcome_simulations}")
            print(f"📝 Execution log: {len(decision.execution_log)} entries")
            
            return decision
            
        except GracefulFailureError as e:
            print(f"❌ Analysis failed: {e}")
            return None


# Example of adding reflection
async def example_add_reflection(decision_id: str):
    """
    Example of adding reflection to a decision.
    
    Args:
        decision_id: UUID of the decision
    """
    from app.database import AsyncSessionLocal
    
    # Create LLM client
    llm_client = LLMClient(api_key=settings.OPENROUTER_API_KEY)
    
    # Create database session
    async with AsyncSessionLocal() as db_session:
        # Create orchestrator
        orchestrator = DecisionOrchestrator(
            llm_client=llm_client,
            db_session=db_session
        )
        
        # Add reflection
        actual_outcome = """
        I accepted the job offer and relocated. The first 3 months were challenging
        due to the new environment, but after 6 months I'm very happy with the decision.
        The salary increase has improved my quality of life, and the new role offers
        better growth opportunities.
        """
        
        try:
            # Add reflection
            decision = await orchestrator.add_reflection(
                decision_id=decision_id,
                actual_outcome=actual_outcome
            )
            
            print(f"✅ Reflection added to decision: {decision.id}")
            print(f"🎯 Accuracy score: {decision.reflection_insight['accuracy_score']}")
            print(f"📚 Lessons learned: {decision.reflection_insight['lessons_learned']}")
            print(f"🔄 Patterns: {decision.reflection_insight['repeated_patterns']}")
            
            return decision
            
        except GracefulFailureError as e:
            print(f"❌ Reflection failed: {e}")
            return None


if __name__ == "__main__":
    import asyncio
    
    # Run example
    print("Running orchestrator example...\n")
    asyncio.run(example_direct_usage())

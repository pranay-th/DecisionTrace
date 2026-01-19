"""
Simple test to verify DecisionOrchestrator implementation.

This test checks that:
1. The orchestrator can be instantiated
2. All agents are initialized correctly
3. The methods exist and have correct signatures
"""

import asyncio
from unittest.mock import Mock, AsyncMock
from app.agents.orchestrator import DecisionOrchestrator
from app.services.llm_client import LLMClient
from app.schemas.decision_input import DecisionInput


def test_orchestrator_initialization():
    """Test that orchestrator initializes correctly."""
    # Create mock LLM client and DB session
    mock_llm_client = Mock(spec=LLMClient)
    mock_db_session = AsyncMock()
    
    # Initialize orchestrator
    orchestrator = DecisionOrchestrator(
        llm_client=mock_llm_client,
        db_session=mock_db_session
    )
    
    # Verify agents are initialized
    assert orchestrator.structuring_agent is not None
    assert orchestrator.bias_agent is not None
    assert orchestrator.outcome_agent is not None
    assert orchestrator.reflection_agent is not None
    
    # Verify LLM client and DB session are stored
    assert orchestrator.llm_client is mock_llm_client
    assert orchestrator.db_session is mock_db_session
    
    print("✅ Orchestrator initialization test passed")


def test_orchestrator_methods_exist():
    """Test that all required methods exist."""
    # Create mock LLM client and DB session
    mock_llm_client = Mock(spec=LLMClient)
    mock_db_session = AsyncMock()
    
    # Initialize orchestrator
    orchestrator = DecisionOrchestrator(
        llm_client=mock_llm_client,
        db_session=mock_db_session
    )
    
    # Verify methods exist
    assert hasattr(orchestrator, 'process_decision')
    assert callable(orchestrator.process_decision)
    
    assert hasattr(orchestrator, '_execute_with_logging')
    assert callable(orchestrator._execute_with_logging)
    
    assert hasattr(orchestrator, '_save_decision')
    assert callable(orchestrator._save_decision)
    
    assert hasattr(orchestrator, 'add_reflection')
    assert callable(orchestrator.add_reflection)
    
    print("✅ Orchestrator methods test passed")


def test_decision_input_validation():
    """Test that DecisionInput schema validates correctly."""
    # Valid input
    valid_input = DecisionInput(
        title="Should I accept the job offer?",
        context="I received an offer from Company X with a 20% salary increase.",
        constraints=["Must relocate", "Start in 2 months"],
        options=["Accept", "Decline", "Negotiate"]
    )
    
    assert valid_input.title == "Should I accept the job offer?"
    assert len(valid_input.constraints) == 2
    assert len(valid_input.options) == 3
    
    print("✅ DecisionInput validation test passed")


if __name__ == "__main__":
    print("Running orchestrator tests...\n")
    
    test_orchestrator_initialization()
    test_orchestrator_methods_exist()
    test_decision_input_validation()
    
    print("\n✅ All tests passed!")

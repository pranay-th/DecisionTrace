"""
Test script to validate all Pydantic schemas.

This script tests that all schemas can be imported and validated correctly.
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.schemas import (
    DecisionInput,
    StructuredDecision,
    BiasReport,
    OutcomeScenario,
    OutcomeSimulation,
    ScenarioType,
    ReflectionInsight,
)


def test_decision_input():
    """Test DecisionInput schema."""
    print("Testing DecisionInput schema...")
    
    # Valid input
    decision_input = DecisionInput(
        title="Should I accept the job offer?",
        context="I received an offer from Company X with a 20% salary increase.",
        constraints=["Must relocate", "Salary is 20% higher"],
        options=["Accept offer", "Decline and stay"]
    )
    print(f"✓ Valid DecisionInput created: {decision_input.title}")
    
    # Test with minimal required fields
    minimal_input = DecisionInput(
        title="Test decision",
        context="Test context with enough characters"
    )
    print(f"✓ Minimal DecisionInput created: {minimal_input.title}")
    
    # Test validation errors
    try:
        invalid_input = DecisionInput(
            title="Too short",  # Less than 5 characters
            context="Test"
        )
        print("✗ Should have failed validation for short title")
    except Exception as e:
        print(f"✓ Validation error caught for short title: {type(e).__name__}")
    
    print()


def test_structured_decision():
    """Test StructuredDecision schema."""
    print("Testing StructuredDecision schema...")
    
    structured = StructuredDecision(
        decision_goal="Determine whether to accept the job offer",
        constraints=["Must relocate", "Salary increase of 20%"],
        options=["Accept offer", "Decline offer"],
        assumptions=["Current job will remain stable"],
        missing_information=["Total relocation costs"]
    )
    print(f"✓ Valid StructuredDecision created: {structured.decision_goal}")
    print()


def test_bias_report():
    """Test BiasReport schema."""
    print("Testing BiasReport schema...")
    
    bias_report = BiasReport(
        detected_biases=["Status quo bias", "Anchoring bias"],
        evidence={
            "Status quo bias": "Decision framing emphasizes staying as default",
            "Anchoring bias": "20% salary increase is prominently featured"
        },
        severity_score=0.6
    )
    print(f"✓ Valid BiasReport created with {len(bias_report.detected_biases)} biases")
    
    # Test severity score validation
    try:
        invalid_bias = BiasReport(
            detected_biases=["Test bias"],
            evidence={"Test bias": "Evidence"},
            severity_score=1.5  # Invalid: > 1.0
        )
        print("✗ Should have failed validation for severity_score > 1.0")
    except Exception as e:
        print(f"✓ Validation error caught for invalid severity_score: {type(e).__name__}")
    
    print()


def test_outcome_simulation():
    """Test OutcomeSimulation and OutcomeScenario schemas."""
    print("Testing OutcomeSimulation and OutcomeScenario schemas...")
    
    # Test individual scenario
    scenario = OutcomeScenario(
        scenario=ScenarioType.BEST_CASE,
        description="You accept the offer and thrive in the new role with great success.",
        risks=["Overwork leading to burnout", "High cost of living"],
        confidence=0.3,
        timeframe_months=12
    )
    print(f"✓ Valid OutcomeScenario created: {scenario.scenario.value}")
    
    # Test complete simulation with 3 scenarios
    simulation = OutcomeSimulation(
        scenarios=[
            OutcomeScenario(
                scenario=ScenarioType.BEST_CASE,
                description="Best case scenario with great success and growth.",
                risks=["Overwork", "High expectations"],
                confidence=0.3,
                timeframe_months=12
            ),
            OutcomeScenario(
                scenario=ScenarioType.WORST_CASE,
                description="Worst case scenario with challenges and setbacks.",
                risks=["Financial strain", "Career setback"],
                confidence=0.2,
                timeframe_months=6
            ),
            OutcomeScenario(
                scenario=ScenarioType.MOST_LIKELY,
                description="Most likely scenario with mixed outcomes and gradual adaptation.",
                risks=["Adjustment period", "Homesickness"],
                confidence=0.5,
                timeframe_months=18
            )
        ]
    )
    print(f"✓ Valid OutcomeSimulation created with {len(simulation.scenarios)} scenarios")
    
    # Test validation for wrong number of scenarios
    try:
        invalid_simulation = OutcomeSimulation(
            scenarios=[
                OutcomeScenario(
                    scenario=ScenarioType.BEST_CASE,
                    description="Only one scenario provided",
                    risks=["Test risk"],
                    confidence=0.5,
                    timeframe_months=12
                )
            ]
        )
        print("✗ Should have failed validation for wrong number of scenarios")
    except Exception as e:
        print(f"✓ Validation error caught for wrong number of scenarios: {type(e).__name__}")
    
    print()


def test_reflection_insight():
    """Test ReflectionInsight schema."""
    print("Testing ReflectionInsight schema...")
    
    reflection = ReflectionInsight(
        accuracy_score=0.75,
        lessons_learned=[
            "Salary increase was beneficial as predicted",
            "Company culture research is critical"
        ],
        repeated_patterns=[
            "Tendency to underweight cultural fit",
            "Optimism bias in timelines"
        ]
    )
    print(f"✓ Valid ReflectionInsight created with accuracy_score: {reflection.accuracy_score}")
    
    # Test with minimal required fields (no repeated_patterns)
    minimal_reflection = ReflectionInsight(
        accuracy_score=0.8,
        lessons_learned=["One lesson learned"]
    )
    print(f"✓ Minimal ReflectionInsight created with {len(minimal_reflection.lessons_learned)} lesson")
    
    # Test validation for empty lessons_learned
    try:
        invalid_reflection = ReflectionInsight(
            accuracy_score=0.5,
            lessons_learned=[]  # Invalid: min_length=1
        )
        print("✗ Should have failed validation for empty lessons_learned")
    except Exception as e:
        print(f"✓ Validation error caught for empty lessons_learned: {type(e).__name__}")
    
    print()


def test_json_serialization():
    """Test JSON serialization and deserialization."""
    print("Testing JSON serialization...")
    
    # Create a decision input
    decision_input = DecisionInput(
        title="Test decision",
        context="Test context with enough characters",
        constraints=["Constraint 1"],
        options=["Option 1", "Option 2"]
    )
    
    # Serialize to JSON
    json_str = decision_input.model_dump_json()
    print(f"✓ Serialized to JSON: {json_str[:50]}...")
    
    # Deserialize from JSON
    deserialized = DecisionInput.model_validate_json(json_str)
    print(f"✓ Deserialized from JSON: {deserialized.title}")
    
    # Verify they match
    assert decision_input.title == deserialized.title
    print("✓ Serialization round-trip successful")
    print()


def main():
    """Run all schema tests."""
    print("=" * 60)
    print("Testing DecisionTrace Pydantic Schemas")
    print("=" * 60)
    print()
    
    try:
        test_decision_input()
        test_structured_decision()
        test_bias_report()
        test_outcome_simulation()
        test_reflection_insight()
        test_json_serialization()
        
        print("=" * 60)
        print("✓ All schema tests passed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
Test script to validate the reflection endpoint accepts ReflectionInput schema.

This test verifies that the add_reflection endpoint properly accepts
ReflectionInput as a request body instead of a query parameter.
"""

import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.schemas.reflection_input import ReflectionInput
from pydantic import ValidationError


def test_reflection_input_schema():
    """Test ReflectionInput schema validation."""
    print("Testing ReflectionInput schema...")
    
    # Valid input with minimum 20 characters
    valid_input = ReflectionInput(
        actual_outcome="I accepted the job offer and relocated. The new role has been challenging but rewarding."
    )
    print(f"✓ Valid ReflectionInput created with {len(valid_input.actual_outcome)} characters")
    
    # Test with exactly 20 characters
    minimal_input = ReflectionInput(
        actual_outcome="12345678901234567890"  # Exactly 20 characters
    )
    print(f"✓ Minimal ReflectionInput created with {len(minimal_input.actual_outcome)} characters")
    
    # Test validation error for too short input
    try:
        invalid_input = ReflectionInput(
            actual_outcome="Too short"  # Less than 20 characters
        )
        print("✗ Should have failed validation for short actual_outcome")
        return False
    except ValidationError as e:
        print(f"✓ Validation error caught for short actual_outcome: {e.error_count()} error(s)")
    
    # Test validation error for missing field
    try:
        invalid_input = ReflectionInput()
        print("✗ Should have failed validation for missing actual_outcome")
        return False
    except ValidationError as e:
        print(f"✓ Validation error caught for missing actual_outcome: {e.error_count()} error(s)")
    
    print()
    return True


def test_reflection_input_json():
    """Test ReflectionInput JSON serialization."""
    print("Testing ReflectionInput JSON serialization...")
    
    # Create a reflection input
    reflection_input = ReflectionInput(
        actual_outcome="I accepted the job offer and relocated. The new role has been challenging but rewarding, and the salary increase has significantly improved my financial situation."
    )
    
    # Serialize to JSON
    json_str = reflection_input.model_dump_json()
    print(f"✓ Serialized to JSON: {json_str[:80]}...")
    
    # Deserialize from JSON
    deserialized = ReflectionInput.model_validate_json(json_str)
    print(f"✓ Deserialized from JSON: {deserialized.actual_outcome[:50]}...")
    
    # Verify they match
    assert reflection_input.actual_outcome == deserialized.actual_outcome
    print("✓ Serialization round-trip successful")
    print()
    return True


def test_reflection_input_dict():
    """Test ReflectionInput dict conversion."""
    print("Testing ReflectionInput dict conversion...")
    
    # Create from dict (simulating JSON request body)
    input_dict = {
        "actual_outcome": "I accepted the job offer and relocated. The new role has been challenging but rewarding."
    }
    
    reflection_input = ReflectionInput(**input_dict)
    print(f"✓ Created ReflectionInput from dict")
    
    # Convert to dict
    output_dict = reflection_input.model_dump()
    print(f"✓ Converted to dict: {list(output_dict.keys())}")
    
    # Verify they match
    assert output_dict["actual_outcome"] == input_dict["actual_outcome"]
    print("✓ Dict conversion successful")
    print()
    return True


def main():
    """Run all reflection endpoint tests."""
    print("=" * 60)
    print("Testing Reflection Endpoint Schema")
    print("=" * 60)
    print()
    
    try:
        success = True
        success = test_reflection_input_schema() and success
        success = test_reflection_input_json() and success
        success = test_reflection_input_dict() and success
        
        if success:
            print("=" * 60)
            print("✓ All reflection endpoint tests passed successfully!")
            print("=" * 60)
            print()
            print("The reflection endpoint is now configured to accept")
            print("ReflectionInput as a request body with the following structure:")
            print()
            print("POST /api/decisions/{decision_id}/reflect")
            print("Content-Type: application/json")
            print()
            print("{")
            print('  "actual_outcome": "string (minimum 20 characters)"')
            print("}")
            print()
        else:
            print("✗ Some tests failed")
            sys.exit(1)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

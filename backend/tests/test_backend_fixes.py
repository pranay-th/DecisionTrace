"""
Test to verify backend fixes for ui-improvements-and-bugfixes spec.

This test verifies:
1. Decision model to_dict() has no duplicate keys
2. Reflection endpoint accepts ReflectionInput as request body
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.models.decision import Decision
from app.api.routes.decisions import add_reflection
from app.schemas.reflection_input import ReflectionInput
import inspect


def test_decision_to_dict_no_duplicates():
    """Test that Decision.to_dict() has no duplicate keys."""
    print("\n" + "=" * 70)
    print("Test 1: Decision.to_dict() has no duplicate keys")
    print("=" * 70)
    
    # Get the source code of to_dict method
    source = inspect.getsource(Decision.to_dict)
    
    # Extract dictionary keys from the return statement
    lines = source.split('\n')
    keys = []
    in_return_dict = False
    
    for line in lines:
        if 'return {' in line:
            in_return_dict = True
        if in_return_dict and '"' in line and ':' in line:
            # Extract key from line like: "key": value,
            key = line.strip().split('"')[1] if '"' in line else None
            if key:
                keys.append(key)
        if in_return_dict and '}' in line:
            break
    
    print(f"Found {len(keys)} keys in to_dict() method:")
    for key in keys:
        print(f"  - {key}")
    
    # Check for duplicates
    from collections import Counter
    counts = Counter(keys)
    duplicates = {k: v for k, v in counts.items() if v > 1}
    
    if duplicates:
        print(f"\n✗ FAILED: Found duplicate keys: {duplicates}")
        return False
    else:
        print(f"\n✓ PASSED: No duplicate keys found!")
        return True


def test_reflection_endpoint_signature():
    """Test that add_reflection endpoint accepts ReflectionInput as request body."""
    print("\n" + "=" * 70)
    print("Test 2: Reflection endpoint accepts ReflectionInput")
    print("=" * 70)
    
    # Get function signature
    sig = inspect.signature(add_reflection)
    params = list(sig.parameters.keys())
    
    print(f"Endpoint parameters: {params}")
    
    # Check for reflection_input parameter
    if 'reflection_input' not in params:
        print("\n✗ FAILED: Missing 'reflection_input' parameter")
        return False
    
    # Check parameter type
    param = sig.parameters['reflection_input']
    param_type = param.annotation
    
    print(f"reflection_input type: {param_type}")
    
    if param_type != ReflectionInput:
        print(f"\n✗ FAILED: Expected ReflectionInput, got {param_type}")
        return False
    
    print("\n✓ PASSED: Endpoint correctly accepts ReflectionInput as request body!")
    return True


def test_reflection_input_validation():
    """Test that ReflectionInput validates correctly."""
    print("\n" + "=" * 70)
    print("Test 3: ReflectionInput validation")
    print("=" * 70)
    
    # Test valid input
    try:
        valid_input = ReflectionInput(
            actual_outcome="This is a valid outcome with more than 20 characters."
        )
        print(f"✓ Valid input accepted: {len(valid_input.actual_outcome)} characters")
    except Exception as e:
        print(f"✗ FAILED: Valid input rejected: {e}")
        return False
    
    # Test invalid input (too short)
    try:
        from pydantic import ValidationError
        invalid_input = ReflectionInput(
            actual_outcome="Too short"
        )
        print("✗ FAILED: Invalid input (too short) was accepted")
        return False
    except ValidationError as e:
        print(f"✓ Invalid input (too short) correctly rejected")
    
    print("\n✓ PASSED: ReflectionInput validation works correctly!")
    return True


def main():
    """Run all backend fix tests."""
    print("\n" + "=" * 70)
    print("BACKEND FIXES VERIFICATION")
    print("Spec: ui-improvements-and-bugfixes")
    print("Task: 3. Checkpoint - Ensure backend fixes work")
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(test_decision_to_dict_no_duplicates())
    results.append(test_reflection_endpoint_signature())
    results.append(test_reflection_input_validation())
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✓ ALL TESTS PASSED!")
        print("\nBackend fixes are working correctly:")
        print("  1. Decision model to_dict() has no duplicate keys")
        print("  2. Reflection endpoint accepts ReflectionInput as request body")
        print("  3. ReflectionInput validates minimum length (20 chars)")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())

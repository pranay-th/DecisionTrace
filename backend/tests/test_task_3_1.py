"""
Integration test for Task 3.1: Create base LLM client

This test verifies that the LLMClient implementation meets all requirements:
- LLMClient class exists in services/llm_client.py
- OpenRouter API integration is configured
- Temperature is set to 0.3
- Max tokens is set to 2000
- Primary model is deepseek/deepseek-chat
- Fallback model is qwen/qwen-2.5-7b-instruct
- Client can make successful API calls
"""

import asyncio
from pydantic import BaseModel, Field
from app.services.llm_client import LLMClient, ModelName, GracefulFailureError
from app.config import settings


class TestResponse(BaseModel):
    """Test response model for verification."""
    answer: str = Field(..., description="A simple answer")


async def test_task_3_1_requirements():
    """Test all requirements for Task 3.1."""
    print("=" * 70)
    print("Task 3.1 Verification: Create base LLM client")
    print("=" * 70)
    
    all_passed = True
    
    # Requirement 1: LLMClient class exists
    print("\n✓ Requirement 1: LLMClient class exists in services/llm_client.py")
    try:
        client = LLMClient()
        print("  ✅ PASSED - LLMClient class instantiated successfully")
    except Exception as e:
        print(f"  ❌ FAILED - Could not instantiate LLMClient: {e}")
        all_passed = False
        return all_passed
    
    # Requirement 2: OpenRouter API integration configured
    print("\n✓ Requirement 2: OpenRouter API integration configured")
    if client.base_url == "https://openrouter.ai/api/v1":
        print(f"  ✅ PASSED - Base URL: {client.base_url}")
    else:
        print(f"  ❌ FAILED - Expected 'https://openrouter.ai/api/v1', got '{client.base_url}'")
        all_passed = False
    
    if client.api_key and client.api_key.startswith("sk-or-"):
        print(f"  ✅ PASSED - API key configured (starts with 'sk-or-')")
    else:
        print(f"  ❌ FAILED - API key not properly configured")
        all_passed = False
    
    # Requirement 3: Temperature set to 0.3
    print("\n✓ Requirement 3: Temperature set to 0.3")
    if client.temperature == 0.3:
        print(f"  ✅ PASSED - Temperature: {client.temperature}")
    else:
        print(f"  ❌ FAILED - Expected 0.3, got {client.temperature}")
        all_passed = False
    
    # Requirement 4: Max tokens set to 2000
    print("\n✓ Requirement 4: Max tokens set to 2000")
    if client.max_tokens == 2000:
        print(f"  ✅ PASSED - Max tokens: {client.max_tokens}")
    else:
        print(f"  ❌ FAILED - Expected 2000, got {client.max_tokens}")
        all_passed = False
    
    # Requirement 5: Primary model is deepseek/deepseek-chat
    print("\n✓ Requirement 5: Primary model is deepseek/deepseek-chat")
    if ModelName.PRIMARY.value == "deepseek/deepseek-chat":
        print(f"  ✅ PASSED - Primary model: {ModelName.PRIMARY.value}")
    else:
        print(f"  ❌ FAILED - Expected 'deepseek/deepseek-chat', got '{ModelName.PRIMARY.value}'")
        all_passed = False
    
    # Requirement 6: Fallback model is qwen/qwen-2.5-7b-instruct
    print("\n✓ Requirement 6: Fallback model is qwen/qwen-2.5-7b-instruct")
    if ModelName.FALLBACK.value == "qwen/qwen-2.5-7b-instruct":
        print(f"  ✅ PASSED - Fallback model: {ModelName.FALLBACK.value}")
    else:
        print(f"  ❌ FAILED - Expected 'qwen/qwen-2.5-7b-instruct', got '{ModelName.FALLBACK.value}'")
        all_passed = False
    
    # Requirement 7: Can make successful API calls
    print("\n✓ Requirement 7: Can make successful API calls to OpenRouter")
    try:
        prompt = """
        Please respond with a JSON object:
        {"answer": "success"}
        
        Return only the JSON, no other text.
        """
        
        result = await client.generate_structured(
            prompt=prompt,
            response_model=TestResponse,
            model=ModelName.PRIMARY
        )
        
        if result.answer:
            print(f"  ✅ PASSED - Successfully called API and got response: {result.answer}")
            print(f"  ✅ Model used: {client.current_model}")
        else:
            print(f"  ❌ FAILED - Got empty response")
            all_passed = False
            
    except Exception as e:
        print(f"  ❌ FAILED - API call failed: {e}")
        all_passed = False
    
    # Requirement 8: Timeout configured
    print("\n✓ Requirement 8: Timeout configured")
    if client.timeout == 60:
        print(f"  ✅ PASSED - Timeout: {client.timeout}s")
    else:
        print(f"  ⚠️  WARNING - Expected 60s, got {client.timeout}s")
    
    # Summary
    print("\n" + "=" * 70)
    print("Task 3.1 Verification Summary")
    print("=" * 70)
    
    if all_passed:
        print("✅ ALL REQUIREMENTS PASSED")
        print("\nTask 3.1 is COMPLETE:")
        print("  ✓ LLMClient class implemented in services/llm_client.py")
        print("  ✓ OpenRouter API integration configured")
        print("  ✓ Temperature set to 0.3")
        print("  ✓ Max tokens set to 2000")
        print("  ✓ Primary model: deepseek/deepseek-chat")
        print("  ✓ Fallback model: qwen/qwen-2.5-7b-instruct")
        print("  ✓ Successfully tested with real API calls")
    else:
        print("❌ SOME REQUIREMENTS FAILED")
        print("\nPlease review the failures above.")
    
    print("=" * 70)
    
    return all_passed


async def main():
    """Run the verification test."""
    passed = await test_task_3_1_requirements()
    return 0 if passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

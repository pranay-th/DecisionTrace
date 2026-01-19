"""
Unit tests for LLM Client (no API calls required).

These tests verify the client logic without making actual API calls.
"""

import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from pydantic import BaseModel, Field, ValidationError
from app.services import LLMClient, ModelName, GracefulFailureError
from app.config import settings


class TestResponse(BaseModel):
    """Test response model."""
    message: str = Field(..., min_length=1)
    count: int = Field(..., ge=0)


async def test_successful_call():
    """Test successful LLM call with valid response."""
    print("\nTest 1: Successful LLM call")
    print("-" * 40)
    
    client = LLMClient(api_key="test-key")
    
    # Mock the _call_openrouter method
    mock_response = '{"message": "Hello", "count": 42}'
    
    with patch.object(client, '_call_openrouter', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_response
        
        result = await client.generate_structured(
            prompt="Test prompt",
            response_model=TestResponse,
            model=ModelName.PRIMARY
        )
        
        assert result.message == "Hello"
        assert result.count == 42
        assert client.current_model == ModelName.PRIMARY.value
        
        # Verify the mock was called
        mock_call.assert_called_once()
        
        print("✅ Successful call works correctly")
        return True


async def test_retry_on_validation_failure():
    """Test retry logic when validation fails."""
    print("\nTest 2: Retry on validation failure")
    print("-" * 40)
    
    client = LLMClient(api_key="test-key")
    
    # First call returns invalid JSON, second call returns valid JSON
    invalid_response = '{"message": "", "count": -1}'  # Fails validation
    valid_response = '{"message": "Hello", "count": 42}'
    
    with patch.object(client, '_call_openrouter', new_callable=AsyncMock) as mock_call:
        mock_call.side_effect = [invalid_response, valid_response]
        
        result = await client.generate_structured(
            prompt="Test prompt",
            response_model=TestResponse,
            model=ModelName.PRIMARY
        )
        
        assert result.message == "Hello"
        assert result.count == 42
        
        # Verify retry happened (called twice)
        assert mock_call.call_count == 2
        
        print("✅ Retry logic works correctly")
        return True


async def test_fallback_on_retry_failure():
    """Test fallback to secondary model when retry fails."""
    print("\nTest 3: Fallback on retry failure")
    print("-" * 40)
    
    client = LLMClient(api_key="test-key")
    
    # Primary model fails twice, fallback succeeds
    invalid_response = '{"message": "", "count": -1}'  # Fails validation
    valid_response = '{"message": "Hello from fallback", "count": 99}'
    
    with patch.object(client, '_call_openrouter', new_callable=AsyncMock) as mock_call:
        # First two calls (primary + retry) fail, third call (fallback) succeeds
        mock_call.side_effect = [invalid_response, invalid_response, valid_response]
        
        result = await client.generate_structured(
            prompt="Test prompt",
            response_model=TestResponse,
            model=ModelName.PRIMARY
        )
        
        assert result.message == "Hello from fallback"
        assert result.count == 99
        
        # Verify fallback happened (called 3 times: primary, retry, fallback)
        assert mock_call.call_count == 3
        
        print("✅ Fallback logic works correctly")
        return True


async def test_graceful_failure():
    """Test GracefulFailureError when all attempts fail."""
    print("\nTest 4: Graceful failure after all attempts")
    print("-" * 40)
    
    client = LLMClient(api_key="test-key")
    
    # All calls return invalid data
    invalid_response = '{"message": "", "count": -1}'
    
    with patch.object(client, '_call_openrouter', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = invalid_response
        
        try:
            result = await client.generate_structured(
                prompt="Test prompt",
                response_model=TestResponse,
                model=ModelName.PRIMARY
            )
            print("❌ Should have raised GracefulFailureError")
            return False
        except GracefulFailureError as e:
            assert "could not be completed reliably" in str(e)
            
            # Verify all attempts were made:
            # - primary (1st attempt)
            # - primary retry (2nd attempt)
            # - fallback (3rd attempt)
            # - fallback retry (4th attempt)
            assert mock_call.call_count == 4
            
            print("✅ Graceful failure works correctly")
            return True


async def test_timeout_handling():
    """Test timeout error handling."""
    print("\nTest 5: Timeout handling")
    print("-" * 40)
    
    client = LLMClient(api_key="test-key")
    
    import httpx
    
    with patch.object(client, '_call_openrouter', new_callable=AsyncMock) as mock_call:
        mock_call.side_effect = httpx.TimeoutException("Request timed out")
        
        try:
            result = await client.generate_structured(
                prompt="Test prompt",
                response_model=TestResponse,
                model=ModelName.PRIMARY
            )
            print("❌ Should have raised GracefulFailureError")
            return False
        except GracefulFailureError as e:
            assert "timed out" in str(e)
            print("✅ Timeout handling works correctly")
            return True


async def test_http_error_handling():
    """Test HTTP error handling."""
    print("\nTest 6: HTTP error handling")
    print("-" * 40)
    
    client = LLMClient(api_key="test-key")
    
    import httpx
    
    with patch.object(client, '_call_openrouter', new_callable=AsyncMock) as mock_call:
        # Create a mock response with 401 status
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_call.side_effect = httpx.HTTPStatusError(
            "401 Unauthorized",
            request=MagicMock(),
            response=mock_response
        )
        
        try:
            result = await client.generate_structured(
                prompt="Test prompt",
                response_model=TestResponse,
                model=ModelName.PRIMARY
            )
            print("❌ Should have raised GracefulFailureError")
            return False
        except GracefulFailureError as e:
            assert "API error" in str(e)
            print("✅ HTTP error handling works correctly")
            return True


async def test_model_configuration():
    """Test model configuration."""
    print("\nTest 7: Model configuration")
    print("-" * 40)
    
    client = LLMClient(api_key="test-key")
    
    # Verify configuration
    assert client.temperature == settings.LLM_TEMPERATURE
    assert client.max_tokens == settings.LLM_MAX_TOKENS
    assert client.timeout == settings.LLM_TIMEOUT
    assert client.base_url == settings.OPENROUTER_BASE_URL
    
    # Verify model names
    assert ModelName.PRIMARY.value == "deepseek/deepseek-chat"
    assert ModelName.FALLBACK.value == "qwen/qwen-2.5-7b-instruct"
    
    print("✅ Model configuration is correct")
    return True


async def test_current_model_tracking():
    """Test that current_model is tracked correctly."""
    print("\nTest 8: Current model tracking")
    print("-" * 40)
    
    client = LLMClient(api_key="test-key")
    
    valid_response = '{"message": "Hello", "count": 42}'
    
    with patch.object(client, '_call_openrouter', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = valid_response
        
        # Test with PRIMARY model
        result = await client.generate_structured(
            prompt="Test prompt",
            response_model=TestResponse,
            model=ModelName.PRIMARY
        )
        assert client.current_model == ModelName.PRIMARY.value
        
        # Test with FALLBACK model
        result = await client.generate_structured(
            prompt="Test prompt",
            response_model=TestResponse,
            model=ModelName.FALLBACK
        )
        assert client.current_model == ModelName.FALLBACK.value
        
        print("✅ Current model tracking works correctly")
        return True


async def main():
    """Run all unit tests."""
    print("=" * 60)
    print("LLM Client Unit Test Suite")
    print("=" * 60)
    print("\nThese tests use mocks and don't require an API key.")
    
    # Run all tests
    tests = [
        test_model_configuration(),
        test_successful_call(),
        test_retry_on_validation_failure(),
        test_fallback_on_retry_failure(),
        test_graceful_failure(),
        test_timeout_handling(),
        test_http_error_handling(),
        test_current_model_tracking(),
    ]
    
    results = await asyncio.gather(*tests, return_exceptions=True)
    
    # Check for exceptions
    failed = []
    for i, result in enumerate(results, 1):
        if isinstance(result, Exception):
            print(f"\n❌ Test {i} raised exception: {result}")
            failed.append(i)
        elif result is False:
            failed.append(i)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {len(tests) - len(failed)}")
    print(f"Failed: {len(failed)}")
    
    if not failed:
        print("\n🎉 All unit tests passed!")
        return 0
    else:
        print(f"\n⚠️  Tests {failed} failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

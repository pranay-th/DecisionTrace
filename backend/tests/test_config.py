"""
Quick test script to verify configuration and logging setup.
Run with: python test_config.py
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.logging_config import configure_logging, get_logger

def test_configuration():
    """Test that configuration loads correctly."""
    print("Testing Configuration...")
    print(f"✓ App Name: {settings.APP_NAME}")
    print(f"✓ App Version: {settings.APP_VERSION}")
    print(f"✓ Primary Model: {settings.PRIMARY_MODEL}")
    print(f"✓ Fallback Model: {settings.FALLBACK_MODEL}")
    print(f"✓ LLM Temperature: {settings.LLM_TEMPERATURE}")
    print(f"✓ Max Tokens: {settings.LLM_MAX_TOKENS}")
    print(f"✓ Log Level: {settings.LOG_LEVEL}")
    print(f"✓ Log Format: {settings.LOG_FORMAT}")
    print(f"✓ Max Retries: {settings.MAX_RETRIES}")
    print(f"✓ Allowed Origins: {settings.ALLOWED_ORIGINS}")
    
    # Check if OpenRouter API key is set
    if settings.OPENROUTER_API_KEY:
        print(f"✓ OpenRouter API Key: {'*' * 20}{settings.OPENROUTER_API_KEY[-4:]}")
    else:
        print("⚠ OpenRouter API Key: Not set (required for production)")
    
    print("\nConfiguration loaded successfully! ✓")


def test_logging():
    """Test that logging is configured correctly."""
    print("\nTesting Logging...")
    
    # Configure logging
    configure_logging()
    
    # Get logger
    logger = get_logger("test")
    
    # Test different log levels
    logger.debug("This is a debug message", test_key="test_value")
    logger.info("This is an info message", test_key="test_value")
    logger.warning("This is a warning message", test_key="test_value")
    
    print("\nLogging configured successfully! ✓")


if __name__ == "__main__":
    print("=" * 60)
    print("DecisionTrace Configuration & Logging Test")
    print("=" * 60)
    print()
    
    try:
        test_configuration()
        test_logging()
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

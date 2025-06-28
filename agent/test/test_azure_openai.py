#!/usr/bin/env python3
"""
Azure OpenAI Configuration Test Script

Test script to validate Azure OpenAI configuration and connection
for the agent system.
"""

import asyncio
import os
import sys
import logging
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from azure_openai_config import (
    load_azure_openai_config, 
    validate_azure_openai_config, 
    get_azure_openai_config_status
)
from azure_openai_client import get_azure_openai_client, call_llm, LLMValidationError
from base_agent import BaseAgent
from db_client import AgentType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestAgent(BaseAgent):
    """Simple test agent for Azure OpenAI testing"""
    
    def __init__(self):
        super().__init__(AgentType.METADATA)
    
    async def _execute_logic(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simple test logic"""
        return {"test": "success", "task": task_description}

async def test_configuration():
    """Test Azure OpenAI configuration loading and validation"""
    
    print("🔧 Testing Azure OpenAI Configuration...")
    print("=" * 50)
    
    # Test configuration loading
    try:
        config = load_azure_openai_config()
        if config:
            print(f"✅ Configuration loaded successfully")
            print(f"   Endpoint: {config.endpoint}")
            print(f"   Deployment: {config.deployment_name}")
            print(f"   API Version: {config.api_version}")
            print(f"   Auth Method: {'Azure AD' if config.use_azure_ad else 'API Key'}")
            print(f"   Has API Key: {bool(config.api_key)}")
        else:
            print("❌ Azure OpenAI not configured")
            return False
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False
    
    # Test configuration validation
    try:
        validation = validate_azure_openai_config()
        if validation["is_valid"]:
            print("✅ Configuration validation passed")
        else:
            print("❌ Configuration validation failed:")
            for error in validation["errors"]:
                print(f"   - {error}")
            for missing in validation["missing_vars"]:
                print(f"   - Missing: {missing}")
            return False
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False
    
    return True

async def test_client_initialization():
    """Test Azure OpenAI client initialization"""
    
    print("\n🚀 Testing Azure OpenAI Client Initialization...")
    print("=" * 50)
    
    try:
        client = await get_azure_openai_client()
        if client.is_ready():
            print("✅ Azure OpenAI client initialized successfully")
            return True
        else:
            print("❌ Azure OpenAI client not ready")
            return False
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return False

async def test_simple_llm_call():
    """Test simple LLM call using the convenience function"""
    
    print("\n💬 Testing Simple LLM Call...")
    print("=" * 50)
    
    try:
        response = await call_llm(
            system_prompt="You are a helpful assistant. Respond briefly and clearly.",
            user_prompt="Say 'Azure OpenAI connection test successful!' and nothing else.",
            max_tokens=50,
            temperature=0.1
        )
        
        print(f"✅ LLM call successful")
        print(f"   Response: {response}")
        return True
        
    except LLMValidationError as e:
        print(f"❌ LLM validation error: {e}")
        return False
    except Exception as e:
        print(f"❌ LLM call failed: {e}")
        return False

async def test_agent_llm_call():
    """Test LLM call through the base agent"""
    
    print("\n🤖 Testing Agent LLM Call...")
    print("=" * 50)
    
    try:
        test_agent = TestAgent()
        
        # Test the standard call_llm method
        response = await test_agent.call_llm(
            system_prompt="You are a helpful test assistant.",
            user_prompt="Respond with 'Agent LLM test successful!' and explain this is a test.",
            max_tokens=100
        )
        
        print(f"✅ Agent LLM call successful")
        print(f"   Response: {response}")
        
        # Test connection validation
        connection_status = await test_agent.validate_azure_openai_connection()
        print(f"✅ Connection validation: {connection_status['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent LLM call failed: {e}")
        return False

async def test_enhanced_llm_call():
    """Test enhanced LLM call with more options"""
    
    print("\n🎛️ Testing Enhanced LLM Call...")
    print("=" * 50)
    
    try:
        test_agent = TestAgent()
        
        response = await test_agent.call_llm_with_options(
            system_prompt="You are a creative assistant.",
            user_prompt="Write a very short poem about Azure OpenAI (max 2 lines).",
            max_tokens=100,
            temperature=0.8
        )
        
        print(f"✅ Enhanced LLM call successful")
        print(f"   Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced LLM call failed: {e}")
        return False

async def run_all_tests():
    """Run all Azure OpenAI tests"""
    
    print("🧪 Azure OpenAI Test Suite")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print()
    
    tests = [
        ("Configuration", test_configuration),
        ("Client Initialization", test_client_initialization),
        ("Simple LLM Call", test_simple_llm_call),
        ("Agent LLM Call", test_agent_llm_call),
        ("Enhanced LLM Call", test_enhanced_llm_call)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Azure OpenAI is configured and working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check your Azure OpenAI configuration.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1) 
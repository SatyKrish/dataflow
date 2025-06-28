"""
pytest configuration for DataFlow agent tests

This file contains pytest fixtures and configuration for testing the agent system.
"""

import pytest
import asyncio
import os
import sys
from typing import Generator

# Add parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import test dependencies
from base_agent import BaseAgent
from db_client import AgentType
from azure_openai_config import load_azure_openai_config

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_agent():
    """Fixture providing a test agent instance"""
    class TestAgent(BaseAgent):
        def __init__(self):
            super().__init__(AgentType.METADATA)
        
        async def _execute_logic(self, task_description: str, context: dict) -> dict:
            return {"test": "success", "task": task_description}
    
    agent = TestAgent()
    yield agent
    await agent.cleanup()

@pytest.fixture
def azure_openai_config():
    """Fixture providing Azure OpenAI configuration"""
    return load_azure_openai_config()

@pytest.fixture
def mock_context():
    """Fixture providing mock context for agent testing"""
    return {
        "user_email": "test@example.com",
        "query": "test query",
        "metadata_results": {"tables": ["test_table"]},
        "entitlement_results": {"access_granted": True}
    }

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment variables if needed"""
    # Set test-specific environment variables
    test_env_vars = {
        "POSTGRES_DB": "test_dataflow_agents",
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_USER": "postgres",
        "POSTGRES_PASSWORD": "postgres"
    }
    
    for key, value in test_env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
    
    yield
    
    # Cleanup if needed
    pass

# Custom markers for different test categories
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "azure_openai: tests that require Azure OpenAI configuration"
    )
    config.addinivalue_line(
        "markers", "integration: integration tests that require external services"
    )
    config.addinivalue_line(
        "markers", "unit: unit tests that don't require external dependencies"
    )
    config.addinivalue_line(
        "markers", "slow: tests that take a long time to run"
    )

# Skip tests based on availability
def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip tests based on configuration"""
    
    # Check if Azure OpenAI is configured
    azure_config = load_azure_openai_config()
    skip_azure = pytest.mark.skip(reason="Azure OpenAI not configured")
    
    for item in items:
        # Skip Azure OpenAI tests if not configured
        if "azure_openai" in item.keywords and not azure_config:
            item.add_marker(skip_azure) 
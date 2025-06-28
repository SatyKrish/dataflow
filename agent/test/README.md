# DataFlow Agent Tests

This directory contains all test modules for the DataFlow agent system, organized into a comprehensive test suite.

## Test Structure

```
test/
├── __init__.py                 # Test package initialization
├── conftest.py                # pytest configuration and fixtures
├── test_runner.py             # Unified test runner
├── test_azure_openai.py       # Azure OpenAI configuration and connection tests
├── test_server.py             # Server endpoint and API tests
├── test_data_agent.py         # Data agent functionality tests
└── README.md                  # This file
```

## Available Tests

### 🔧 Azure OpenAI Tests (`test_azure_openai.py`)
Tests the Azure OpenAI integration and configuration:
- Configuration loading and validation
- Client initialization (both Azure AD and API key auth)
- LLM calling functionality
- Enhanced features and error handling

### 🌐 Server Tests (`test_server.py`)
Tests the FastAPI server endpoints:
- Health check endpoint
- Azure OpenAI status endpoint
- Agent listing endpoint
- Research execution endpoint

### 🤖 Data Agent Tests (`test_data_agent.py`)
Tests the data agent functionality:
- MCP configuration loading
- Tool discovery from MCP servers
- LLM-based tool selection
- Full execution simulation

## Running Tests

### Quick Start

Run all tests:
```bash
cd agent/test
python test_runner.py
```

### Individual Test Modules

Run specific test modules:
```bash
# Azure OpenAI tests
python test_runner.py azure_openai

# Server tests (requires server to be running)
python test_runner.py server

# Data agent tests
python test_runner.py data_agent
```

### Direct Execution

You can also run test files directly:
```bash
python test_azure_openai.py
python test_server.py
python test_data_agent.py
```

### Using pytest

Run with pytest for advanced features:
```bash
# Install pytest if not already installed
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run with markers
pytest -m "azure_openai"
pytest -m "integration"
pytest -m "unit"

# Run specific test file
pytest test_azure_openai.py
```

## Test Categories (pytest markers)

- `@pytest.mark.azure_openai` - Tests requiring Azure OpenAI configuration
- `@pytest.mark.integration` - Integration tests requiring external services
- `@pytest.mark.unit` - Unit tests with no external dependencies
- `@pytest.mark.slow` - Tests that take longer to execute

## Test Utilities

### Test Runner Features
```bash
# List available tests
python test_runner.py --list

# Quick health check
python test_runner.py --health

# Help
python test_runner.py --help
```

### Fixtures Available (pytest)
- `test_agent` - Provides a test agent instance
- `azure_openai_config` - Azure OpenAI configuration object
- `mock_context` - Mock context for agent testing
- `event_loop` - Async event loop for session

## Prerequisites

### For Azure OpenAI Tests
Set environment variables:
```bash
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT_NAME="your-deployment"
# Optional (if not set, Azure AD auth is used):
export AZURE_OPENAI_API_KEY="your-api-key"
```

### For Server Tests
Start the agent server:
```bash
cd agent
python server.py
```

### For Data Agent Tests
Configure MCP servers in `mcp_config.json` or ensure demo servers are available.

## Debugging Test Failures

1. **Azure OpenAI Tests Failing**:
   - Check environment variables
   - Verify Azure OpenAI endpoint and deployment
   - Test network connectivity

2. **Server Tests Failing**:
   - Ensure server is running: `python agent/server.py`
   - Check port availability (default: 8001)

3. **Data Agent Tests Failing**:
   - Check MCP configuration
   - Verify MCP servers are running
   - Review tool discovery logs

## Adding New Tests

### Structure for New Test Files
```python
#!/usr/bin/env python3
"""
Description of what this test module covers
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Your test imports and code here

async def run_all_tests():
    """Main test runner function"""
    # Test implementation
    pass

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
```

### Register New Tests
Add your test module to `test_runner.py`:
```python
self.test_modules = {
    # ... existing tests
    "your_test": {
        "module": your_test_module,
        "function": your_test_module.run_all_tests,
        "description": "Description of your test"
    }
}
```

## Test Output

All tests provide structured output with:
- ✅ Success indicators
- ❌ Failure indicators  
- ⚠️ Warning indicators
- 📊 Summary statistics
- 🎉 Completion messages

Example output:
```
🧪 Azure OpenAI Test Suite
==================================================
🔧 Testing Azure OpenAI Configuration...
✅ Configuration loaded successfully
✅ Configuration validation passed

🚀 Testing Azure OpenAI Client Initialization...
✅ Azure OpenAI client initialized successfully

📊 Test Results Summary
==================================================
Configuration: ✅ PASSED
Client Initialization: ✅ PASSED
Simple LLM Call: ✅ PASSED
Agent LLM Call: ✅ PASSED
Enhanced LLM Call: ✅ PASSED

Overall: 5/5 tests passed
🎉 All tests passed! Azure OpenAI is configured and working correctly.
```

## Continuous Integration

The test suite is designed to work well in CI/CD environments:
- Proper exit codes (0 for success, 1 for failure)
- Clear output formatting
- Environment-based test skipping
- Timeout handling for network operations

## Performance Considerations

- Tests use async/await for optimal performance
- Connection pooling where applicable
- Reasonable timeouts for external services
- Parallel execution where safe 
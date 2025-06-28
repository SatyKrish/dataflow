# Azure OpenAI Integration for DataFlow Agents

This document describes the enhanced Azure OpenAI integration for the DataFlow agent system, providing robust authentication options and improved error handling.

## Overview

The agent system now uses the same Azure OpenAI configuration pattern as the chat interface, supporting both Azure AD authentication and API key authentication with proper validation and error handling.

## Features

- **Dual Authentication Support**: Both Azure AD (managed identity/service principal) and API key authentication
- **Automatic Authentication Detection**: Automatically chooses the appropriate authentication method based on configuration
- **Robust Error Handling**: Comprehensive error handling with specific validation errors
- **Configuration Validation**: Built-in validation for Azure OpenAI configuration
- **Connection Testing**: Built-in connection testing capabilities
- **Backward Compatibility**: Maintains compatibility with existing agent code

## Configuration

### Environment Variables

The system uses the following environment variables (same as the chat interface):

```bash
# Required
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name

# Optional
AZURE_OPENAI_API_VERSION=2024-10-21  # Default value
AZURE_OPENAI_API_KEY=your-api-key     # If not provided, Azure AD is used
```

### Authentication Methods

#### 1. Azure AD Authentication (Recommended for Production)
- **Configuration**: Simply omit the `AZURE_OPENAI_API_KEY` environment variable
- **Authentication**: Uses `DefaultAzureCredential` for automatic credential discovery
- **Supports**: Managed Identity, Service Principal, Azure CLI, etc.

```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
# No API key = Azure AD authentication
```

#### 2. API Key Authentication
- **Configuration**: Provide the `AZURE_OPENAI_API_KEY` environment variable
- **Authentication**: Uses the provided API key directly

```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_KEY=your-api-key-here
```

## Usage

### Basic Usage (Existing Agent Code)

Existing agents continue to work without changes:

```python
from base_agent import BaseAgent
from db_client import AgentType

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentType.METADATA)
    
    async def _execute_logic(self, task_description: str, context: dict) -> dict:
        # Use LLM with existing interface
        response = await self.call_llm(
            system_prompt="You are a helpful assistant.",
            user_prompt="Analyze this data...",
            max_tokens=1000
        )
        return {"analysis": response}
```

### Enhanced Usage

New enhanced methods are available:

```python
# Enhanced LLM call with more options
response = await self.call_llm_with_options(
    system_prompt="You are a creative assistant.",
    user_prompt="Generate ideas...",
    max_tokens=1500,
    temperature=0.8
)

# Connection validation
connection_status = await self.validate_azure_openai_connection()
if connection_status["status"] == "connected":
    print("Azure OpenAI is working!")
```

### Direct Client Usage

For advanced scenarios, you can use the client directly:

```python
from azure_openai_client import get_azure_openai_client, LLMChatOptions, LLMMessage

# Get the global client
client = await get_azure_openai_client()

# Create chat completion
options = LLMChatOptions(
    messages=[
        LLMMessage(role="system", content="You are a helpful assistant."),
        LLMMessage(role="user", content="Hello, Azure OpenAI!")
    ],
    max_tokens=100,
    temperature=0.7
)

response = await client.create_chat_completion(options)
print(response.content)
```

## Testing and Validation

### Configuration Testing

Use the provided test script to validate your configuration:

```bash
cd agent
python test_azure_openai.py
```

The test script will:
- ✅ Validate configuration loading
- ✅ Test client initialization  
- ✅ Test simple LLM calls
- ✅ Test agent LLM integration
- ✅ Test enhanced LLM features

### Server Endpoint

The agent server now includes an Azure OpenAI status endpoint:

```bash
curl http://localhost:8001/azure-openai/status
```

This returns detailed status information including:
- Configuration status
- Validation results
- Connection test results
- Authentication method being used

## Error Handling

The system provides comprehensive error handling:

### Configuration Errors
- Missing required environment variables
- Invalid endpoint URLs
- Missing deployment names

### Authentication Errors
- Invalid API keys
- Azure AD authentication failures
- Token acquisition failures

### API Errors
- Network connectivity issues
- Rate limiting
- Service unavailability

### Example Error Handling

```python
from azure_openai_client import LLMValidationError

try:
    response = await self.call_llm(system_prompt, user_prompt)
except LLMValidationError as e:
    logger.error(f"Azure OpenAI validation error: {e}")
    # Handle configuration or authentication issues
except Exception as e:
    logger.error(f"General LLM error: {e}")
    # Handle other errors
```

## Migration from Previous Implementation

The new implementation is fully backward compatible. No changes are required to existing agent code.

### What Changed
- ✅ Enhanced authentication options (Azure AD + API key)
- ✅ Better error handling and validation
- ✅ Improved configuration management
- ✅ Added connection testing
- ✅ Better logging and monitoring

### What Stayed the Same
- ✅ All existing `call_llm()` interfaces
- ✅ Agent initialization patterns
- ✅ Environment variable names
- ✅ Response formats

## Troubleshooting

### Common Issues

1. **"Azure OpenAI not configured"**
   - Check that `AZURE_OPENAI_ENDPOINT` is set
   - Verify the endpoint URL format

2. **"API key is required when not using Azure AD authentication"**
   - Either provide `AZURE_OPENAI_API_KEY` or ensure Azure AD is properly configured
   - For Azure AD: ensure appropriate credentials are available

3. **"Azure OpenAI client not initialized"**
   - Run the test script to diagnose initialization issues
   - Check logs for specific error details

4. **"Chat completion failed"**
   - Verify network connectivity to Azure OpenAI
   - Check deployment name and model availability
   - Verify API quotas and rate limits

### Debugging Steps

1. **Run the test script**: `python test_azure_openai.py`
2. **Check the status endpoint**: `curl http://localhost:8001/azure-openai/status`
3. **Review application logs**: Look for Azure OpenAI related log messages
4. **Validate environment variables**: Ensure all required variables are set correctly

## Dependencies

The following additional dependencies were added:

```
azure-identity>=1.15.0
azure-core>=1.29.0
```

These are automatically included in the updated `requirements.txt`.

## Security Considerations

### Azure AD Authentication (Recommended)
- Uses managed identity or service principal
- No secrets in environment variables
- Automatic token rotation
- Audit trail through Azure AD

### API Key Authentication
- Store API keys securely (Azure Key Vault, etc.)
- Rotate keys regularly
- Monitor usage and access

### Network Security
- Use private endpoints when possible
- Configure network access restrictions
- Monitor API usage and access patterns

## Performance Considerations

- **Connection Pooling**: The client uses connection pooling for optimal performance
- **Global Client**: A single global client instance is shared across agents
- **Async Operations**: All operations are fully asynchronous
- **Error Recovery**: Built-in retry and error recovery mechanisms

## Support

For issues or questions:
1. Check this documentation
2. Run the test script for diagnostics
3. Review application logs
4. Check the Azure OpenAI service status
5. Verify Azure AD permissions (if using Azure AD authentication) 
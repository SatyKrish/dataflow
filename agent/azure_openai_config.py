#!/usr/bin/env python3
"""
Azure OpenAI Configuration for Agent System

Handles loading and validation of Azure OpenAI settings from environment variables,
following the same pattern as the chat section.
"""

import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AzureOpenAIConfig:
    """Azure OpenAI configuration data class"""
    endpoint: str
    deployment_name: str
    api_version: str = "2024-10-21"
    api_key: Optional[str] = None
    use_azure_ad: bool = False

def load_azure_openai_config() -> Optional[AzureOpenAIConfig]:
    """
    Load Azure OpenAI configuration from environment variables
    Returns None if not configured
    """
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") or os.getenv("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")

    # If endpoint is not provided, Azure OpenAI is not configured
    if not endpoint:
        logger.info("ℹ️ Azure OpenAI not configured (no endpoint provided)")
        return None

    # Validate required fields
    if not deployment_name:
        raise ValueError("AZURE_OPENAI_DEPLOYMENT_NAME or AZURE_OPENAI_DEPLOYMENT is required when Azure OpenAI endpoint is configured")

    # Automatically determine authentication method: if API key is provided, use it; otherwise use Azure AD
    use_azure_ad = not bool(api_key)

    config = AzureOpenAIConfig(
        endpoint=endpoint,
        deployment_name=deployment_name,
        api_version=api_version,
        api_key=api_key,
        use_azure_ad=use_azure_ad
    )

    logger.info("✅ Azure OpenAI configuration loaded from environment variables", extra={
        "endpoint": config.endpoint,
        "deployment_name": config.deployment_name,
        "api_version": config.api_version,
        "auth_method": "Azure AD" if use_azure_ad else "API Key",
        "has_api_key": bool(config.api_key)
    })

    return config

def validate_azure_openai_config() -> Dict[str, Any]:
    """
    Validate Azure OpenAI environment variables
    Returns validation status with details
    """
    errors = []
    missing_vars = []

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") or os.getenv("AZURE_OPENAI_DEPLOYMENT")

    # Check if Azure OpenAI is configured at all
    if not endpoint:
        return {"is_valid": True, "missing_vars": [], "errors": []}  # Not configured is valid

    # Validate endpoint format
    if not endpoint.startswith("https://") or "openai.azure.com" not in endpoint:
        errors.append("AZURE_OPENAI_ENDPOINT must be a valid Azure OpenAI endpoint URL")

    # Validate deployment name
    if not deployment_name:
        missing_vars.append("AZURE_OPENAI_DEPLOYMENT_NAME or AZURE_OPENAI_DEPLOYMENT")

    # Note: No authentication validation needed - if no API key, Azure AD will be used automatically

    return {
        "is_valid": len(missing_vars) == 0 and len(errors) == 0,
        "missing_vars": missing_vars,
        "errors": errors
    }

def get_azure_openai_config_status() -> Dict[str, Any]:
    """
    Get Azure OpenAI configuration status for display
    """
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") or os.getenv("AZURE_OPENAI_DEPLOYMENT")

    if not endpoint:
        return {
            "configured": False,
            "auth_method": "none"
        }

    # Automatically determine auth method: API key takes precedence, otherwise Azure AD
    auth_method = "api-key" if api_key else "azure-ad"

    return {
        "configured": True,
        "auth_method": auth_method,
        "endpoint": endpoint,
        "deployment_name": deployment_name
    } 
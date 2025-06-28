#!/usr/bin/env python3
"""
Azure OpenAI Client for Agent System

Pure Azure OpenAI LLM Client that handles only LLM interactions,
supporting both Azure AD and API key authentication.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

from openai import AsyncAzureOpenAI
from azure.identity.aio import DefaultAzureCredential
from azure.core.credentials import AccessToken

from azure_openai_config import AzureOpenAIConfig, load_azure_openai_config

logger = logging.getLogger(__name__)

@dataclass
class LLMMessage:
    """LLM message structure"""
    role: str  # 'user', 'assistant', 'system'
    content: str

@dataclass
class LLMChatOptions:
    """LLM chat completion options"""
    messages: List[LLMMessage]
    max_tokens: Optional[int] = 2000
    temperature: Optional[float] = 0.7
    stream: bool = False

@dataclass
class LLMChatResponse:
    """LLM chat completion response"""
    content: Optional[str] = None
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, int]] = None

class LLMValidationError(Exception):
    """Custom exception for LLM validation errors"""
    def __init__(self, message: str, details: Any = None):
        super().__init__(message)
        self.details = details

class AzureOpenAIClient:
    """Azure OpenAI client with support for both authentication methods"""
    
    def __init__(self, config: Optional[AzureOpenAIConfig] = None):
        self.config = config or load_azure_openai_config()
        self.client: Optional[AsyncAzureOpenAI] = None
        self._azure_credential: Optional[DefaultAzureCredential] = None
        
        if not self.config:
            raise LLMValidationError("Azure OpenAI configuration not found")
    
    async def initialize(self) -> None:
        """Initialize Azure OpenAI client with appropriate authentication"""
        try:
            if self.config.use_azure_ad:
                # Use Azure AD authentication (managed identity or service principal)
                self._azure_credential = DefaultAzureCredential()
                
                # For Azure AD, we need to get tokens manually and create client without explicit auth
                self.client = AsyncAzureOpenAI(
                    azure_endpoint=self.config.endpoint,
                    api_version=self.config.api_version,
                    azure_ad_token_provider=self._get_azure_ad_token
                )
            else:
                # Use API key authentication
                if not self.config.api_key:
                    raise LLMValidationError("API key is required when not using Azure AD authentication")
                
                self.client = AsyncAzureOpenAI(
                    api_key=self.config.api_key,
                    azure_endpoint=self.config.endpoint,
                    api_version=self.config.api_version
                )
            
            logger.info("✅ Azure OpenAI LLM client initialized successfully")
            
        except Exception as error:
            logger.error(f"❌ Failed to initialize Azure OpenAI LLM client: {error}")
            raise LLMValidationError(f"Azure OpenAI LLM client initialization failed: {error}")
    
    async def _get_azure_ad_token(self) -> str:
        """Get Azure AD token for authentication"""
        if not self._azure_credential:
            raise LLMValidationError("Azure credential not initialized")
        
        scope = "https://cognitiveservices.azure.com/.default"
        token = await self._azure_credential.get_token(scope)
        return token.token
    
    async def create_chat_completion(self, options: LLMChatOptions) -> LLMChatResponse:
        """Create chat completion with the configured model"""
        if not self.client:
            raise LLMValidationError("Azure OpenAI client not initialized")
        
        try:
            # Format messages for OpenAI API
            messages = [
                {"role": msg.role, "content": msg.content}
                for msg in options.messages
            ]
            
            response = await self.client.chat.completions.create(
                model=self.config.deployment_name,
                messages=messages,
                max_tokens=options.max_tokens,
                temperature=options.temperature,
                stream=options.stream
            )
            
            choice = response.choices[0] if response.choices else None
            if not choice:
                raise LLMValidationError("No response choice received from Azure OpenAI")
            
            return LLMChatResponse(
                content=choice.message.content,
                finish_reason=choice.finish_reason,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                } if response.usage else None
            )
            
        except Exception as error:
            logger.error(f"❌ Azure OpenAI API error: {error}")
            raise LLMValidationError(f"Chat completion failed: {error}")
    
    async def create_streaming_chat_completion(self, options: LLMChatOptions):
        """Create streaming chat completion"""
        if not self.client:
            raise LLMValidationError("Azure OpenAI client not initialized")
        
        try:
            # Format messages for OpenAI API
            messages = [
                {"role": msg.role, "content": msg.content}
                for msg in options.messages
            ]
            
            stream = await self.client.chat.completions.create(
                model=self.config.deployment_name,
                messages=messages,
                max_tokens=options.max_tokens,
                temperature=options.temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield LLMChatResponse(
                        content=chunk.choices[0].delta.content,
                        finish_reason=chunk.choices[0].finish_reason
                    )
                    
        except Exception as error:
            logger.error(f"❌ Azure OpenAI streaming API error: {error}")
            raise LLMValidationError(f"Streaming chat completion failed: {error}")
    
    def is_ready(self) -> bool:
        """Check if client is ready for use"""
        return self.client is not None
    
    async def close(self) -> None:
        """Clean up resources"""
        if self.client:
            await self.client.close()
        if self._azure_credential:
            await self._azure_credential.close()

# Global client instance
_global_client: Optional[AzureOpenAIClient] = None

async def get_azure_openai_client() -> AzureOpenAIClient:
    """Get or create the global Azure OpenAI client instance"""
    global _global_client
    
    if _global_client is None:
        _global_client = AzureOpenAIClient()
        await _global_client.initialize()
    
    return _global_client

async def call_llm(
    system_prompt: str, 
    user_prompt: str, 
    max_tokens: int = 1000,
    temperature: float = 0.3
) -> str:
    """
    Convenience function for simple LLM calls
    Compatible with the existing base_agent.call_llm interface
    """
    client = await get_azure_openai_client()
    
    options = LLMChatOptions(
        messages=[
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt)
        ],
        max_tokens=max_tokens,
        temperature=temperature
    )
    
    response = await client.create_chat_completion(options)
    return response.content or "" 
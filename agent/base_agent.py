#!/usr/bin/env python3
"""
Base Agent Implementation for Multi-Agent Research System

Provides the abstract base class and common functionality for all specialized agents.
"""

import os
import asyncio
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from abc import ABC, abstractmethod
import logging
import httpx

from azure_openai_client import call_llm as azure_call_llm, get_azure_openai_client, LLMValidationError
from azure_openai_config import validate_azure_openai_config, get_azure_openai_config_status
from db_client import db_client, AgentType, ExecutionStatus

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all subagents"""
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.http_client = httpx.AsyncClient(timeout=60.0)
        
        # Validate Azure OpenAI configuration on initialization
        validation = validate_azure_openai_config()
        if not validation["is_valid"]:
            logger.warning(f"Azure OpenAI configuration validation failed: {validation}")
        
        # Log configuration status
        status = get_azure_openai_config_status()
        if status["configured"]:
            logger.info(f"Azure OpenAI configured with {status['auth_method']} authentication")
        else:
            logger.warning("Azure OpenAI not configured")
    
    async def execute(
        self, 
        session_id: str, 
        task_description: str, 
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute the agent task with full tracking"""
        
        start_time = time.time()
        context = context or {}
        
        # Create execution record
        execution_id = await db_client.create_subagent_execution(
            session_id=session_id,
            agent_type=self.agent_type,
            task_description=task_description
        )
        
        try:
            logger.info(f"{self.agent_type.value} agent starting execution: {execution_id}")
            
            # Execute the actual agent logic
            results = await self._execute_logic(task_description, context)
            
            # Calculate execution time
            execution_time = int((time.time() - start_time) * 1000)
            
            # Update execution as completed
            await db_client.update_subagent_execution(
                execution_id=execution_id,
                status=ExecutionStatus.COMPLETED,
                results=results,
                execution_time_ms=execution_time
            )
            
            logger.info(f"{self.agent_type.value} agent completed in {execution_time}ms")
            
            return {
                "execution_id": execution_id,
                "status": "completed",
                "results": results,
                "execution_time_ms": execution_time,
                "summary": results.get("summary", f"{self.agent_type.value} agent completed successfully")
            }
            
        except Exception as e:
            # Update execution as failed
            error_msg = str(e)
            execution_time = int((time.time() - start_time) * 1000)
            
            await db_client.update_subagent_execution(
                execution_id=execution_id,
                status=ExecutionStatus.FAILED,
                execution_time_ms=execution_time,
                error_message=error_msg
            )
            
            logger.error(f"{self.agent_type.value} agent failed: {error_msg}")
            
            return {
                "execution_id": execution_id,
                "status": "failed", 
                "error": error_msg,
                "execution_time_ms": execution_time,
                "summary": f"{self.agent_type.value} agent failed: {error_msg}"
            }
    
    @abstractmethod
    async def _execute_logic(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Implement the specific agent logic"""
        pass
    
    async def call_llm(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
        """
        Helper method to call Azure OpenAI using the new client
        Maintains backward compatibility with existing agents
        """
        try:
            response = await azure_call_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=max_tokens,
                temperature=0.3
            )
            return response
        except LLMValidationError as e:
            logger.error(f"Azure OpenAI LLM call failed: {e}")
            raise
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    async def call_llm_with_options(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        max_tokens: int = 1000,
        temperature: float = 0.3
    ) -> str:
        """
        Enhanced LLM calling method with more options
        """
        try:
            response = await azure_call_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response
        except LLMValidationError as e:
            logger.error(f"Azure OpenAI LLM call failed: {e}")
            raise
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    async def validate_azure_openai_connection(self) -> Dict[str, Any]:
        """
        Validate that Azure OpenAI connection is working
        Returns connection status and details
        """
        try:
            client = await get_azure_openai_client()
            if client.is_ready():
                # Test with a simple call
                test_response = await self.call_llm(
                    system_prompt="You are a helpful assistant.",
                    user_prompt="Say 'Connection test successful'",
                    max_tokens=50
                )
                
                return {
                    "status": "connected",
                    "message": "Azure OpenAI connection successful",
                    "test_response": test_response,
                    "config_status": get_azure_openai_config_status()
                }
            else:
                return {
                    "status": "not_ready",
                    "message": "Azure OpenAI client not ready",
                    "config_status": get_azure_openai_config_status()
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Azure OpenAI connection failed: {str(e)}",
                "config_status": get_azure_openai_config_status(),
                "validation": validate_azure_openai_config()
            }
    
    async def cleanup(self):
        """Clean up resources used by the agent"""
        if hasattr(self, 'http_client') and self.http_client:
            await self.http_client.aclose()
    
    def __del__(self):
        """Cleanup on garbage collection"""
        if hasattr(self, 'http_client') and self.http_client:
            try:
                asyncio.create_task(self.http_client.aclose())
            except Exception:
                pass  # Ignore cleanup errors during garbage collection 
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

from openai import AsyncAzureOpenAI
from db_client import db_client, AgentType, ExecutionStatus

logger = logging.getLogger(__name__)

# Initialize Azure OpenAI client
openai_client = AsyncAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

class BaseAgent(ABC):
    """Base class for all subagents"""
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.http_client = httpx.AsyncClient(timeout=60.0)
    
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
                "execution_time_ms": execution_time
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
                "execution_time_ms": execution_time
            }
    
    @abstractmethod
    async def _execute_logic(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Implement the specific agent logic"""
        pass
    
    async def call_llm(self, system_prompt: str, user_prompt: str, max_tokens: int = 1000) -> str:
        """Helper method to call Azure OpenAI"""
        try:
            response = await openai_client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise 
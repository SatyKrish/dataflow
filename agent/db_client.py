#!/usr/bin/env python3
"""
Database client for Langraph Agents
Simplified version for agent operations
"""

import os
import asyncio
import asyncpg
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class SessionStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed" 
    FAILED = "failed"
    CANCELLED = "cancelled"

class AgentType(Enum):
    METADATA = "metadata"
    ENTITLEMENT = "entitlement"
    DATA = "data"
    AGGREGATION = "aggregation"

class ExecutionStatus(Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class DatabaseClient:
    """PostgreSQL client for langraph agents"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'database': os.getenv('POSTGRES_DB', 'dataflow_agents'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
            'min_size': 2,
            'max_size': 10
        }
    
    async def connect(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(**self.config)
            logger.info("Database connection pool created")
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
    
    async def create_subagent_execution(
        self,
        session_id: str,
        agent_type: AgentType,
        task_description: str,
        tool_calls: Optional[Dict] = None
    ) -> str:
        """Create new subagent execution record"""
        query = """
            INSERT INTO subagent_executions (session_id, agent_type, task_description, tool_calls)
            VALUES ($1, $2, $3, $4)
            RETURNING execution_id
        """
        calls_json = json.dumps(tool_calls) if tool_calls else None
        
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, session_id, agent_type.value, task_description, calls_json)
    
    async def update_subagent_execution(
        self,
        execution_id: str,
        status: Optional[ExecutionStatus] = None,
        results: Optional[Dict] = None,
        execution_time_ms: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Update subagent execution"""
        updates = []
        params = []
        param_idx = 1
        
        if status:
            updates.append(f"status = ${param_idx}")
            params.append(status.value)
            param_idx += 1
            
        if status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
            updates.append(f"completed_at = ${param_idx}")
            params.append(datetime.utcnow())
            param_idx += 1
            
        if results:
            updates.append(f"results = ${param_idx}")
            params.append(json.dumps(results))
            param_idx += 1
            
        if execution_time_ms is not None:
            updates.append(f"execution_time_ms = ${param_idx}")
            params.append(execution_time_ms)
            param_idx += 1
            
        if error_message:
            updates.append(f"error_message = ${param_idx}")
            params.append(error_message)
            param_idx += 1
        
        if not updates:
            return False
            
        query = f"""
            UPDATE subagent_executions 
            SET {', '.join(updates)}
            WHERE execution_id = ${param_idx}
        """
        params.append(execution_id)
        
        async with self.pool.acquire() as conn:
            result = await conn.execute(query, *params)
            return result.split()[-1] == '1'

# Global database client instance
db_client = DatabaseClient() 
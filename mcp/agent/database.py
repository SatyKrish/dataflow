#!/usr/bin/env python3
"""
Database client for Multi-Agent Research System
Handles PostgreSQL connections and operations for agent coordination
"""

import os
import asyncio
import asyncpg
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
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

class MemoryType(Enum):
    RESEARCH_PLAN = "research_plan"
    INTERMEDIATE_RESULTS = "intermediate_results"
    CONTEXT_SUMMARY = "context_summary"
    ARTIFACT_REFERENCE = "artifact_reference"

@dataclass
class ResearchSession:
    session_id: str
    user_id: str
    initial_query: str
    research_plan: Optional[Dict] = None
    final_outcome: Optional[Dict] = None
    token_usage: int = 0
    session_duration: Optional[timedelta] = None
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

@dataclass
class SubagentExecution:
    execution_id: str
    session_id: str
    agent_type: AgentType
    task_description: str
    tool_calls: Optional[Dict] = None
    results: Optional[Dict] = None
    status: ExecutionStatus = ExecutionStatus.RUNNING
    execution_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

@dataclass
class SessionMemory:
    memory_id: str
    session_id: str
    memory_type: MemoryType
    content: Optional[Dict] = None
    artifact_path: Optional[str] = None
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class DatabaseClient:
    """PostgreSQL client for multi-agent system coordination"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
        self.config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'database': os.getenv('POSTGRES_DB', 'dataflow_agents'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
            'min_size': 5,
            'max_size': 20
        }
    
    async def connect(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(**self.config)
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    async def execute_query(self, query: str, *args) -> Any:
        """Execute a query and return result"""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def execute_single(self, query: str, *args) -> Any:
        """Execute a query and return single result"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def execute_value(self, query: str, *args) -> Any:
        """Execute a query and return single value"""
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)
    
    # User Management
    async def get_or_create_user(self, email: str, name: str = None) -> str:
        """Get existing user or create new one"""
        query = """
            INSERT INTO users (email, name) 
            VALUES ($1, $2)
            ON CONFLICT (email) DO UPDATE SET 
                name = COALESCE(EXCLUDED.name, users.name),
                updated_at = NOW()
            RETURNING user_id
        """
        return await self.execute_value(query, email, name)
    
    # Research Sessions
    async def create_research_session(
        self, 
        user_id: str, 
        initial_query: str,
        research_plan: Optional[Dict] = None
    ) -> str:
        """Create a new research session"""
        query = """
            INSERT INTO research_sessions (user_id, initial_query, research_plan)
            VALUES ($1, $2, $3)
            RETURNING session_id
        """
        plan_json = json.dumps(research_plan) if research_plan else None
        return await self.execute_value(query, user_id, initial_query, plan_json)
    
    async def update_research_session(
        self,
        session_id: str,
        status: Optional[SessionStatus] = None,
        research_plan: Optional[Dict] = None,
        final_outcome: Optional[Dict] = None,
        token_usage: Optional[int] = None
    ) -> bool:
        """Update research session"""
        updates = []
        params = []
        param_idx = 1
        
        if status:
            updates.append(f"status = ${param_idx}")
            params.append(status.value)
            param_idx += 1
            
        if status in [SessionStatus.COMPLETED, SessionStatus.FAILED, SessionStatus.CANCELLED]:
            updates.append(f"completed_at = ${param_idx}")
            params.append(datetime.utcnow())
            param_idx += 1
            
        if research_plan:
            updates.append(f"research_plan = ${param_idx}")
            params.append(json.dumps(research_plan))
            param_idx += 1
            
        if final_outcome:
            updates.append(f"final_outcome = ${param_idx}")
            params.append(json.dumps(final_outcome))
            param_idx += 1
            
        if token_usage is not None:
            updates.append(f"token_usage = ${param_idx}")
            params.append(token_usage)
            param_idx += 1
        
        if not updates:
            return False
            
        query = f"""
            UPDATE research_sessions 
            SET {', '.join(updates)}
            WHERE session_id = ${param_idx}
        """
        params.append(session_id)
        
        async with self.pool.acquire() as conn:
            result = await conn.execute(query, *params)
            return result.split()[-1] == '1'
    
    async def get_research_session(self, session_id: str) -> Optional[ResearchSession]:
        """Get research session by ID"""
        query = """
            SELECT session_id, user_id, initial_query, research_plan, final_outcome,
                   token_usage, session_duration, status, created_at, completed_at
            FROM research_sessions 
            WHERE session_id = $1
        """
        row = await self.execute_single(query, session_id)
        if not row:
            return None
            
        return ResearchSession(
            session_id=row['session_id'],
            user_id=row['user_id'],
            initial_query=row['initial_query'],
            research_plan=json.loads(row['research_plan']) if row['research_plan'] else None,
            final_outcome=json.loads(row['final_outcome']) if row['final_outcome'] else None,
            token_usage=row['token_usage'],
            session_duration=row['session_duration'],
            status=SessionStatus(row['status']),
            created_at=row['created_at'],
            completed_at=row['completed_at']
        )
    
    # Subagent Executions
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
        return await self.execute_value(query, session_id, agent_type.value, task_description, calls_json)
    
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
    
    async def get_session_executions(self, session_id: str) -> List[SubagentExecution]:
        """Get all subagent executions for a session"""
        query = """
            SELECT execution_id, session_id, agent_type, task_description, tool_calls, 
                   results, status, execution_time_ms, error_message, created_at, completed_at
            FROM subagent_executions 
            WHERE session_id = $1
            ORDER BY created_at
        """
        rows = await self.execute_query(query, session_id)
        
        executions = []
        for row in rows:
            executions.append(SubagentExecution(
                execution_id=row['execution_id'],
                session_id=row['session_id'],
                agent_type=AgentType(row['agent_type']),
                task_description=row['task_description'],
                tool_calls=json.loads(row['tool_calls']) if row['tool_calls'] else None,
                results=json.loads(row['results']) if row['results'] else None,
                status=ExecutionStatus(row['status']),
                execution_time_ms=row['execution_time_ms'],
                error_message=row['error_message'],
                created_at=row['created_at'],
                completed_at=row['completed_at']
            ))
        
        return executions
    
    # Session Memory
    async def store_session_memory(
        self,
        session_id: str,
        memory_type: MemoryType,
        content: Optional[Dict] = None,
        artifact_path: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> str:
        """Store session memory"""
        query = """
            INSERT INTO session_memory (session_id, memory_type, content, artifact_path, expires_at)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING memory_id
        """
        content_json = json.dumps(content) if content else None
        return await self.execute_value(query, session_id, memory_type.value, content_json, artifact_path, expires_at)
    
    async def get_session_memory(
        self, 
        session_id: str, 
        memory_type: Optional[MemoryType] = None
    ) -> List[SessionMemory]:
        """Get session memory, optionally filtered by type"""
        if memory_type:
            query = """
                SELECT memory_id, session_id, memory_type, content, artifact_path, created_at, expires_at
                FROM session_memory 
                WHERE session_id = $1 AND memory_type = $2
                AND (expires_at IS NULL OR expires_at > NOW())
                ORDER BY created_at DESC
            """
            rows = await self.execute_query(query, session_id, memory_type.value)
        else:
            query = """
                SELECT memory_id, session_id, memory_type, content, artifact_path, created_at, expires_at
                FROM session_memory 
                WHERE session_id = $1
                AND (expires_at IS NULL OR expires_at > NOW())
                ORDER BY created_at DESC
            """
            rows = await self.execute_query(query, session_id)
        
        memories = []
        for row in rows:
            memories.append(SessionMemory(
                memory_id=row['memory_id'],
                session_id=row['session_id'],
                memory_type=MemoryType(row['memory_type']),
                content=json.loads(row['content']) if row['content'] else None,
                artifact_path=row['artifact_path'],
                created_at=row['created_at'],
                expires_at=row['expires_at']
            ))
        
        return memories
    
    # Analytics and Monitoring
    async def get_session_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get session analytics for the last N days"""
        query = """
            SELECT 
                COUNT(*) as total_sessions,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_sessions,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_sessions,
                AVG(token_usage) as avg_token_usage,
                AVG(EXTRACT(EPOCH FROM session_duration)) as avg_duration_seconds
            FROM research_sessions 
            WHERE created_at > NOW() - INTERVAL '%s days'
        """ % days
        
        row = await self.execute_single(query)
        
        # Get subagent performance
        subagent_query = """
            SELECT 
                agent_type,
                COUNT(*) as total_executions,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_executions,
                AVG(execution_time_ms) as avg_execution_time_ms
            FROM subagent_executions 
            WHERE created_at > NOW() - INTERVAL '%s days'
            GROUP BY agent_type
        """ % days
        
        subagent_rows = await self.execute_query(subagent_query)
        
        return {
            'session_stats': dict(row),
            'subagent_stats': [dict(row) for row in subagent_rows]
        }

# Global database client instance
db_client = DatabaseClient() 
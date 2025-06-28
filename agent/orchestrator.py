#!/usr/bin/env python3
"""
Multi-Agent Research Orchestrator

Coordinates specialized subagents to execute research tasks in parallel.
This is a simplified orchestrator that will be enhanced with Langraph in Phase 2.
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from db_client import db_client, AgentType
from agent_registry import create_agent
from metadata_agent import MetadataAgent
from entitlement_agent import EntitlementAgent
from data_agent import DataAgent
from aggregation_agent import AggregationAgent

logger = logging.getLogger(__name__)

class ResearchOrchestrator:
    """Orchestrates multi-agent research execution"""
    
    def __init__(self):
        self.agents = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all subagents"""
        self.agents = {
            AgentType.METADATA: MetadataAgent(),
            AgentType.ENTITLEMENT: EntitlementAgent(),
            AgentType.DATA: DataAgent(),
            AgentType.AGGREGATION: AggregationAgent()
        }
        logger.info("Initialized all subagents")
    
    async def execute_research(
        self, 
        session_id: str, 
        query: str, 
        research_mode: str = "full",
        user_email: str = "default@example.com"
    ) -> Dict[str, Any]:
        """Execute multi-agent research based on the query and mode"""
        
        logger.info(f"Starting research orchestration for session: {session_id}")
        start_time = time.time()
        
        try:
            # Initialize database connection if needed
            if not db_client.pool:
                await db_client.connect()
            
            # Develop execution plan based on research mode
            execution_plan = await self._develop_execution_plan(query, research_mode)
            
            # Execute agents based on plan
            agent_results = await self._execute_agents(
                session_id=session_id,
                query=query,
                execution_plan=execution_plan,
                user_email=user_email
            )
            
            # Calculate total execution time and tokens
            total_execution_time = int((time.time() - start_time) * 1000)
            total_tokens = sum(result.get("token_estimate", 500) for result in agent_results.values())
            
            # Prepare final results
            final_results = {
                "session_id": session_id,
                "query": query,
                "research_mode": research_mode,
                "execution_plan": execution_plan,
                "agent_results": agent_results,
                "total_execution_time_ms": total_execution_time,
                "total_tokens": total_tokens,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Research orchestration completed in {total_execution_time}ms")
            return final_results
            
        except Exception as e:
            logger.error(f"Research orchestration failed: {e}")
            raise
    
    async def _develop_execution_plan(self, query: str, research_mode: str) -> Dict[str, Any]:
        """Develop execution plan based on query and mode"""
        
        # Simple execution plans for MVP
        if research_mode == "metadata":
            return {
                "phases": [
                    {"agents": [AgentType.METADATA], "parallel": False}
                ],
                "description": "Metadata discovery only"
            }
        elif research_mode == "data": 
            return {
                "phases": [
                    {"agents": [AgentType.METADATA, AgentType.ENTITLEMENT], "parallel": True},
                    {"agents": [AgentType.DATA], "parallel": False}
                ],
                "description": "Data retrieval with validation"
            }
        elif research_mode == "analysis":
            return {
                "phases": [
                    {"agents": [AgentType.METADATA, AgentType.ENTITLEMENT], "parallel": True},
                    {"agents": [AgentType.DATA], "parallel": False},
                    {"agents": [AgentType.AGGREGATION], "parallel": False}
                ],
                "description": "Full analysis with synthesis"
            }
        else:  # full mode
            return {
                "phases": [
                    {"agents": [AgentType.METADATA, AgentType.ENTITLEMENT], "parallel": True},
                    {"agents": [AgentType.DATA], "parallel": False},
                    {"agents": [AgentType.AGGREGATION], "parallel": False}
                ],
                "description": "Complete multi-agent research"
            }
    
    async def _execute_agents(
        self, 
        session_id: str, 
        query: str, 
        execution_plan: Dict[str, Any],
        user_email: str
    ) -> Dict[str, Any]:
        """Execute agents according to the execution plan"""
        
        agent_results = {}
        context = {
            "query": query,
            "user_email": user_email,
            "session_id": session_id
        }
        
        # Execute each phase in order
        for phase_idx, phase in enumerate(execution_plan["phases"]):
            logger.info(f"Executing phase {phase_idx + 1}: {phase['agents']}")
            
            if phase["parallel"]:
                # Execute agents in parallel
                phase_results = await self._execute_parallel_agents(
                    session_id, phase["agents"], query, context
                )
            else:
                # Execute agents sequentially
                phase_results = await self._execute_sequential_agents(
                    session_id, phase["agents"], query, context
                )
            
            # Merge results and update context
            agent_results.update(phase_results)
            
            # Update context with results for next phase
            if AgentType.METADATA in phase["agents"]:
                context["metadata_results"] = phase_results.get(AgentType.METADATA.value, {})
            if AgentType.ENTITLEMENT in phase["agents"]:
                context["entitlement_results"] = phase_results.get(AgentType.ENTITLEMENT.value, {})
            if AgentType.DATA in phase["agents"]:
                context["data_results"] = phase_results.get(AgentType.DATA.value, {})
        
        return agent_results
    
    async def _execute_parallel_agents(
        self, 
        session_id: str, 
        agent_types: List[AgentType], 
        query: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute multiple agents in parallel"""
        
        # Create tasks for parallel execution
        tasks = []
        for agent_type in agent_types:
            agent = self.agents[agent_type]
            task_description = self._generate_task_description(agent_type, query)
            
            task = asyncio.create_task(
                agent.execute(session_id, task_description, context.copy())
            )
            tasks.append((agent_type, task))
        
        # Wait for all tasks to complete
        results = {}
        for agent_type, task in tasks:
            try:
                result = await task
                results[agent_type.value] = result
                logger.info(f"{agent_type.value} agent completed successfully")
            except Exception as e:
                logger.error(f"{agent_type.value} agent failed: {e}")
                results[agent_type.value] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        return results
    
    async def _execute_sequential_agents(
        self, 
        session_id: str, 
        agent_types: List[AgentType], 
        query: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute agents sequentially"""
        
        results = {}
        for agent_type in agent_types:
            try:
                agent = self.agents[agent_type]
                task_description = self._generate_task_description(agent_type, query)
                
                result = await agent.execute(session_id, task_description, context.copy())
                results[agent_type.value] = result
                
                logger.info(f"{agent_type.value} agent completed successfully")
                
                # Update context with this agent's results for next agent
                if agent_type == AgentType.METADATA:
                    context["metadata_results"] = result.get("results", {})
                elif agent_type == AgentType.ENTITLEMENT:
                    context["entitlement_results"] = result.get("results", {})
                elif agent_type == AgentType.DATA:
                    context["data_results"] = result.get("results", {})
                
            except Exception as e:
                logger.error(f"{agent_type.value} agent failed: {e}")
                results[agent_type.value] = {
                    "status": "failed",
                    "error": str(e)
                }
        
        return results
    
    def _generate_task_description(self, agent_type: AgentType, query: str) -> str:
        """Generate specific task descriptions for each agent type"""
        
        if agent_type == AgentType.METADATA:
            return f"Discover metadata and schemas relevant to: {query}"
        elif agent_type == AgentType.ENTITLEMENT:
            return f"Validate data access permissions for: {query}"
        elif agent_type == AgentType.DATA:
            return f"Retrieve and process data for: {query}"
        elif agent_type == AgentType.AGGREGATION:
            return f"Synthesize research findings for: {query}"
        else:
            return f"Execute research task: {query}"
    
    async def health_check(self) -> Dict[str, Any]:
        """Check orchestrator and agent health"""
        
        health_status = {
            "orchestrator_status": "healthy",
            "agents_initialized": len(self.agents),
            "timestamp": datetime.now().isoformat()
        }
        
        # Test database connection
        try:
            if not db_client.pool:
                await db_client.connect()
            
            test_result = await db_client.execute_value("SELECT 1")
            health_status["database_status"] = "connected" if test_result == 1 else "error"
        except Exception as e:
            health_status["database_status"] = f"error: {str(e)}"
        
        return health_status

# Global orchestrator instance
orchestrator = ResearchOrchestrator() 
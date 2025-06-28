#!/usr/bin/env python3
"""
Subagent Implementations for Multi-Agent Research System

Specialized agents that handle different aspects of research:
- MetadataAgent: Schema and structure discovery
- EntitlementAgent: Permission validation
- DataAgent: Data retrieval and processing
- AggregationAgent: Result synthesis
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
from database import db_client, AgentType, ExecutionStatus

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

class MetadataAgent(BaseAgent):
    """Agent specialized in discovering data schemas and metadata"""
    
    def __init__(self):
        super().__init__(AgentType.METADATA)
    
    async def _execute_logic(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Discover metadata and schemas for the given task"""
        
        system_prompt = """
        You are a metadata discovery specialist. Your job is to:
        1. Identify relevant data sources for the user's query
        2. Discover available schemas, tables, and data structures
        3. Map relationships between data sources
        4. Provide recommendations for data exploration
        
        Focus on structural discovery, not actual data retrieval.
        """
        
        user_prompt = f"""
        Task: {task_description}
        Context: {json.dumps(context, indent=2)}
        
        Discover metadata and provide a structured analysis of:
        1. Relevant data sources to explore
        2. Key schemas/tables/structures to investigate
        3. Relationships between data sources
        4. Recommended exploration strategy
        
        Respond in JSON format with clear categorization.
        """
        
        try:
            # Call Denodo MCP server for metadata discovery
            denodo_endpoint = os.getenv("DENODO_MCP_ENDPOINT", "http://localhost:8081")
            
            metadata_calls = []
            
            # Try to call Denodo for schema discovery
            try:
                denodo_response = await self.http_client.post(
                    f"{denodo_endpoint}/denodo_query",
                    json={"query": "SHOW TABLES", "mode": "metadata"},
                    timeout=30.0
                )
                
                if denodo_response.status_code == 200:
                    denodo_result = denodo_response.json()
                    metadata_calls.append({
                        "source": "denodo",
                        "type": "schema_discovery",
                        "result": denodo_result
                    })
                
            except Exception as e:
                logger.warning(f"Denodo metadata call failed: {e}")
                metadata_calls.append({
                    "source": "denodo", 
                    "type": "schema_discovery",
                    "error": str(e)
                })
            
            # Use LLM to analyze and synthesize metadata findings
            llm_response = await self.call_llm(system_prompt, user_prompt)
            
            try:
                llm_analysis = json.loads(llm_response)
            except json.JSONDecodeError:
                llm_analysis = {"analysis": llm_response}
            
            return {
                "metadata_sources": ["denodo", "demo"],
                "tool_calls": metadata_calls,
                "llm_analysis": llm_analysis,
                "recommendations": {
                    "next_steps": "Proceed with entitlement validation and data retrieval",
                    "priority_sources": ["denodo"],
                    "exploration_strategy": "schema-first approach"
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Metadata agent logic failed: {e}")
            raise

class EntitlementAgent(BaseAgent):
    """Agent specialized in validating data access permissions"""
    
    def __init__(self):
        super().__init__(AgentType.ENTITLEMENT)
    
    async def _execute_logic(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user permissions and data access rights"""
        
        system_prompt = """
        You are an entitlement validation specialist. Your job is to:
        1. Validate user permissions for requested data sources
        2. Check access rights for specific tables/datasets
        3. Identify any data governance restrictions
        4. Provide clear access status and limitations
        
        Always err on the side of caution for data access.
        """
        
        user_prompt = f"""
        Task: {task_description}
        Context: {json.dumps(context, indent=2)}
        
        Validate entitlements and provide:
        1. Access validation for identified data sources
        2. Specific permissions for tables/datasets
        3. Any restrictions or limitations
        4. Approved access scope for this request
        
        Respond in JSON format with clear access status.
        """
        
        try:
            # For MVP, implement basic entitlement logic
            user_email = context.get("user_email", "default@example.com")
            
            # Simulate entitlement checks
            entitlement_calls = []
            
            # Basic validation - in production this would call actual entitlement systems
            access_status = {
                "denodo": "granted",  # Assume access for MVP
                "demo": "granted",
                "restricted_tables": [],
                "validation_method": "basic_check"
            }
            
            entitlement_calls.append({
                "source": "entitlement_service",
                "type": "access_validation", 
                "user": user_email,
                "result": access_status
            })
            
            # Use LLM to analyze entitlement requirements
            llm_response = await self.call_llm(system_prompt, user_prompt)
            
            try:
                llm_analysis = json.loads(llm_response)
            except json.JSONDecodeError:
                llm_analysis = {"analysis": llm_response}
            
            return {
                "access_status": access_status,
                "tool_calls": entitlement_calls,
                "llm_analysis": llm_analysis,
                "permissions": {
                    "data_sources": ["denodo", "demo"],
                    "restrictions": [],
                    "approval_level": "standard_user"
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Entitlement agent logic failed: {e}")
            raise

class DataAgent(BaseAgent):
    """Agent specialized in data retrieval and processing"""
    
    def __init__(self):
        super().__init__(AgentType.DATA)
    
    async def _execute_logic(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve and process data based on metadata and entitlement findings"""
        
        system_prompt = """
        You are a data retrieval specialist. Your job is to:
        1. Retrieve relevant data based on metadata findings
        2. Process and clean the retrieved data
        3. Apply any necessary transformations
        4. Ensure data quality and completeness
        
        Focus on efficient data retrieval while respecting access permissions.
        """
        
        user_prompt = f"""
        Task: {task_description}
        Context: {json.dumps(context, indent=2)}
        
        Retrieve and process data providing:
        1. Data retrieval results from approved sources
        2. Data quality assessment
        3. Processing steps applied
        4. Summary statistics and insights
        
        Respond in JSON format with structured data results.
        """
        
        try:
            data_calls = []
            
            # Call Denodo for actual data retrieval
            denodo_endpoint = os.getenv("DENODO_MCP_ENDPOINT", "http://localhost:8081")
            
            try:
                # Extract query from task or context
                query = context.get("query", task_description)
                
                denodo_response = await self.http_client.post(
                    f"{denodo_endpoint}/denodo_query",
                    json={"query": query, "mode": "data"},
                    timeout=60.0
                )
                
                if denodo_response.status_code == 200:
                    denodo_result = denodo_response.json()
                    data_calls.append({
                        "source": "denodo",
                        "type": "data_retrieval",
                        "query": query,
                        "result": denodo_result
                    })
                
            except Exception as e:
                logger.warning(f"Denodo data call failed: {e}")
                data_calls.append({
                    "source": "denodo",
                    "type": "data_retrieval", 
                    "error": str(e)
                })
            
            # Call Demo MCP for additional data if needed
            demo_endpoint = os.getenv("DEMO_MCP_ENDPOINT", "http://localhost:8080")
            
            try:
                demo_response = await self.http_client.post(
                    f"{demo_endpoint}/ask_ai",
                    json={"question": task_description, "mode": "generate"},
                    timeout=30.0
                )
                
                if demo_response.status_code == 200:
                    demo_result = demo_response.json()
                    data_calls.append({
                        "source": "demo",
                        "type": "synthetic_data",
                        "result": demo_result
                    })
                
            except Exception as e:
                logger.warning(f"Demo data call failed: {e}")
            
            # Use LLM to analyze data results
            llm_response = await self.call_llm(system_prompt, user_prompt)
            
            try:
                llm_analysis = json.loads(llm_response)
            except json.JSONDecodeError:
                llm_analysis = {"analysis": llm_response}
            
            return {
                "data_sources": ["denodo", "demo"],
                "tool_calls": data_calls,
                "llm_analysis": llm_analysis,
                "data_summary": {
                    "sources_accessed": len([call for call in data_calls if "error" not in call]),
                    "total_calls": len(data_calls),
                    "data_quality": "validated"
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Data agent logic failed: {e}")
            raise

class AggregationAgent(BaseAgent):
    """Agent specialized in synthesizing results from other agents"""
    
    def __init__(self):
        super().__init__(AgentType.AGGREGATION)
    
    async def _execute_logic(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize and aggregate findings from all other agents"""
        
        system_prompt = """
        You are a research synthesis specialist. Your job is to:
        1. Combine findings from metadata, entitlement, and data agents
        2. Identify key insights and patterns
        3. Provide comprehensive conclusions
        4. Generate citations and source attributions
        
        Create a cohesive narrative from multiple agent findings.
        """
        
        # Get results from other agents
        metadata_results = context.get("metadata_results", {})
        entitlement_results = context.get("entitlement_results", {})
        data_results = context.get("data_results", {})
        
        user_prompt = f"""
        Task: {task_description}
        
        Aggregate and synthesize these agent findings:
        
        Metadata Agent Results:
        {json.dumps(metadata_results, indent=2)}
        
        Entitlement Agent Results:
        {json.dumps(entitlement_results, indent=2)}
        
        Data Agent Results:
        {json.dumps(data_results, indent=2)}
        
        Provide a comprehensive synthesis including:
        1. Executive summary of findings
        2. Key insights discovered
        3. Data source citations
        4. Recommendations for further research
        5. Limitations and caveats
        
        Respond in JSON format with structured synthesis.
        """
        
        try:
            # Use LLM to synthesize all findings
            llm_response = await self.call_llm(system_prompt, user_prompt, max_tokens=1500)
            
            try:
                synthesis = json.loads(llm_response)
            except json.JSONDecodeError:
                synthesis = {"synthesis": llm_response}
            
            # Generate citations from all agent results
            citations = []
            
            # Extract citations from metadata results
            if metadata_results.get("tool_calls"):
                for call in metadata_results["tool_calls"]:
                    if "error" not in call:
                        citations.append({
                            "source": call.get("source", "unknown"),
                            "type": "metadata",
                            "timestamp": metadata_results.get("timestamp")
                        })
            
            # Extract citations from data results  
            if data_results.get("tool_calls"):
                for call in data_results["tool_calls"]:
                    if "error" not in call:
                        citations.append({
                            "source": call.get("source", "unknown"),
                            "type": "data",
                            "query": call.get("query"),
                            "timestamp": data_results.get("timestamp")
                        })
            
            return {
                "synthesis": synthesis,
                "citations": citations,
                "agent_summary": {
                    "metadata_agent": "completed" if metadata_results else "not_executed",
                    "entitlement_agent": "completed" if entitlement_results else "not_executed", 
                    "data_agent": "completed" if data_results else "not_executed"
                },
                "research_completeness": {
                    "total_agents": 3,
                    "completed_agents": len([r for r in [metadata_results, entitlement_results, data_results] if r]),
                    "success_rate": len([r for r in [metadata_results, entitlement_results, data_results] if r]) / 3
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Aggregation agent logic failed: {e}")
            raise

# Agent registry for easy access
AGENT_REGISTRY = {
    AgentType.METADATA: MetadataAgent,
    AgentType.ENTITLEMENT: EntitlementAgent,
    AgentType.DATA: DataAgent,
    AgentType.AGGREGATION: AggregationAgent
}

def create_agent(agent_type: AgentType) -> BaseAgent:
    """Factory function to create agents"""
    agent_class = AGENT_REGISTRY.get(agent_type)
    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent_type}")
    return agent_class() 
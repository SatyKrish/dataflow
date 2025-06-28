#!/usr/bin/env python3
"""
Metadata Agent Implementation

Specialized agent for discovering data schemas and metadata structures.
Handles schema discovery, data source mapping, and relationship identification.
"""

import os
import json
import logging
from typing import Dict, Any
from datetime import datetime

from base_agent import BaseAgent
from db_client import AgentType

logger = logging.getLogger(__name__)

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
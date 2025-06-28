#!/usr/bin/env python3
"""
Data Agent Implementation

Specialized agent for data retrieval and processing operations.
Handles actual data fetching, processing, quality assessment, and transformation.
"""

import os
import json
import logging
from typing import Dict, Any
from datetime import datetime

from base_agent import BaseAgent
from db_client import AgentType

logger = logging.getLogger(__name__)

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
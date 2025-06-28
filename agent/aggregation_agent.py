#!/usr/bin/env python3
"""
Aggregation Agent Implementation

Specialized agent for synthesizing and aggregating results from other agents.
Handles combining findings, generating insights, and providing comprehensive conclusions.
"""

import json
import logging
from typing import Dict, Any
from datetime import datetime

from base_agent import BaseAgent
from db_client import AgentType

logger = logging.getLogger(__name__)

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
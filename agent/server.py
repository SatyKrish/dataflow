#!/usr/bin/env python3
"""
Multi-Agent Research Server

FastAPI server that exposes HTTP endpoints for LangGraph-based research agents.
This server is called by the MCP server to execute multi-agent research tasks.
"""

import os
import asyncio
import logging
import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from langgraph_orchestrator import LangGraphOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize LangGraph orchestrator
orchestrator = LangGraphOrchestrator()

# Create FastAPI app
app = FastAPI(
    title="LangGraph Multi-Agent Research System",
    description="LangGraph-based multi-agent research coordination with intelligent workflows",
    version="2.0.0"
)

# Request/Response models
class ResearchRequest(BaseModel):
    query: str
    user_email: str = "default@example.com"
    session_id: Optional[str] = None

class ResearchResponse(BaseModel):
    session_id: str
    status: str
    results: Dict[str, Any]
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    agents: Dict[str, str]
    timestamp: str

@app.post("/research", response_model=ResearchResponse)
async def execute_research(request: ResearchRequest):
    """Execute multi-agent research using LangGraph workflow"""
    
    logger.info(f"Research request: {request.query[:100]}...")
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Execute research using LangGraph orchestrator
        results = await orchestrator.process_request(
            task_description=request.query,
            user_email=request.user_email,
            query=request.query
        )
        
        return ResearchResponse(
            session_id=session_id,
            status=results.get("workflow_status", "completed"),
            results=results,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Research execution failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Research execution failed: {str(e)}"
        )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check system health status"""
    
    try:
        return HealthResponse(
            status="healthy",
            agents={
                "metadata_agent": "ready",
                "entitlement_agent": "ready", 
                "data_agent": "ready",
                "aggregation_agent": "ready",
                "supervisor": "ready"
            },
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )

@app.get("/")
async def root():
    """Root endpoint with basic information"""
    return {
        "service": "LangGraph Multi-Agent Research System",
        "version": "2.0.0",
        "status": "running",
        "framework": "LangGraph",
        "endpoints": {
            "research": "/research",
            "health": "/health",
            "agents": "/agents"
        }
    }

@app.get("/agents")
async def list_agents():
    """List available agents and their LLM-powered capabilities"""
    return {
        "framework": "LangGraph StateGraph with Command handoffs",
        "workflow_pattern": "Supervisor with LLM decision-making",
        "agents": {
            "supervisor": {
                "type": "coordinator",
                "description": "LLM-powered workflow supervisor",
                "capabilities": [
                    "intelligent_agent_selection",
                    "workflow_coordination", 
                    "error_recovery",
                    "state_management"
                ]
            },
            "metadata_agent": {
                "type": "specialist",
                "description": "LLM-powered metadata discovery strategist",
                "capabilities": [
                    "strategic_discovery_planning",
                    "intelligent_method_selection",
                    "adaptive_metadata_exploration",
                    "metadata_quality_assessment"
                ]
            },
            "entitlement_agent": {
                "type": "specialist", 
                "description": "LLM-powered security reasoning specialist",
                "capabilities": [
                    "security_threat_analysis",
                    "compliance_requirement_reasoning",
                    "multi_dimensional_risk_assessment",
                    "intelligent_access_control_decisions"
                ]
            },
            "data_agent": {
                "type": "specialist",
                "description": "LLM-powered data tool orchestrator",
                "capabilities": [
                    "dynamic_mcp_tool_discovery",
                    "intelligent_tool_selection",
                    "adaptive_execution_strategies",
                    "cross_source_result_synthesis"
                ]
            },
            "aggregation_agent": {
                "type": "specialist",
                "description": "LLM-powered strategic data analyst",
                "capabilities": [
                    "intelligent_pattern_recognition",
                    "business_insight_generation",
                    "strategic_recommendation_creation",
                    "comprehensive_analytical_synthesis"
                ]
            }
        },
        "features": {
            "state_management": "LangGraph MessagesState with typed fields",
            "handoffs": "Command-based agent transitions",
            "communication": "Message-based agent interaction",
            "error_handling": "Intelligent recovery and fallback",
            "workflow_control": "LLM-supervised execution flow"
        }
    }

if __name__ == "__main__":
    # Configuration
    host = os.getenv("AGENT_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("AGENT_SERVER_PORT", 8001))
    
    logger.info(f"Starting LangGraph Multi-Agent Research Server on {host}:{port}")
    
    uvicorn.run(
        "server:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    ) 
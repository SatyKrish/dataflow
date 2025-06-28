#!/usr/bin/env python3
"""
Multi-Agent Research Server

FastAPI server that exposes HTTP endpoints for the langraph-based research agents.
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

from orchestrator import orchestrator
from database import db_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Multi-Agent Research System",
    description="Langraph-based multi-agent research coordination",
    version="1.0.0"
)

# Request/Response models
class ResearchRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    research_mode: str = "full"
    user_email: str = "default@example.com"

class ResearchResponse(BaseModel):
    session_id: str
    status: str
    results: Dict[str, Any]
    execution_time_ms: int
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    components: Dict[str, Any]
    timestamp: str

@app.on_event("startup")
async def startup_event():
    """Initialize database connections on startup"""
    try:
        await db_client.connect()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        # Continue without database for basic functionality

@app.on_event("shutdown") 
async def shutdown_event():
    """Clean up connections on shutdown"""
    try:
        await db_client.disconnect()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

@app.post("/execute_research", response_model=ResearchResponse)
async def execute_research(request: ResearchRequest):
    """Execute multi-agent research for the given query"""
    
    logger.info(f"Research request received: {request.query[:100]}...")
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Execute research using orchestrator
        results = await orchestrator.execute_research(
            session_id=session_id,
            query=request.query,
            research_mode=request.research_mode,
            user_email=request.user_email
        )
        
        return ResearchResponse(
            session_id=session_id,
            status="completed",
            results=results,
            execution_time_ms=results.get("total_execution_time_ms", 0),
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
        # Check orchestrator health
        orchestrator_health = await orchestrator.health_check()
        
        components = {
            "orchestrator": orchestrator_health,
            "fastapi_server": {
                "status": "healthy",
                "version": "1.0.0"
            }
        }
        
        # Determine overall status
        overall_status = "healthy"
        if orchestrator_health.get("database_status", "").startswith("error"):
            overall_status = "degraded"
        
        return HealthResponse(
            status=overall_status,
            components=components,
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
        "service": "Multi-Agent Research System",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "execute_research": "/execute_research",
            "health": "/health"
        }
    }

@app.get("/agents")
async def list_agents():
    """List available agents and their capabilities"""
    return {
        "agents": {
            "metadata": {
                "description": "Discovers data schemas and metadata",
                "capabilities": ["schema_discovery", "data_source_mapping"]
            },
            "entitlement": {
                "description": "Validates data access permissions",
                "capabilities": ["access_validation", "permission_checking"]
            },
            "data": {
                "description": "Retrieves and processes data",
                "capabilities": ["data_retrieval", "data_processing"]
            },
            "aggregation": {
                "description": "Synthesizes research findings",
                "capabilities": ["result_synthesis", "citation_generation"]
            }
        },
        "research_modes": ["metadata", "data", "analysis", "full"]
    }

if __name__ == "__main__":
    # Configuration
    host = os.getenv("AGENT_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("AGENT_SERVER_PORT", 8001))
    
    logger.info(f"Starting Multi-Agent Research Server on {host}:{port}")
    
    uvicorn.run(
        "server:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    ) 
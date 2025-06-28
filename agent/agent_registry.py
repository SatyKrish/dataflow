#!/usr/bin/env python3
"""
Agent Registry and Factory

Centralized registry for all agent types and factory function for creating agents.
Provides easy access to all available agents and maintains the mapping between
agent types and their implementations.
"""

from db_client import AgentType
from base_agent import BaseAgent
from metadata_agent import MetadataAgent
from entitlement_agent import EntitlementAgent
from data_agent import DataAgent
from aggregation_agent import AggregationAgent

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

def get_available_agent_types():
    """Get list of all available agent types"""
    return list(AGENT_REGISTRY.keys())

def get_agent_class(agent_type: AgentType):
    """Get the agent class for a given agent type"""
    return AGENT_REGISTRY.get(agent_type) 
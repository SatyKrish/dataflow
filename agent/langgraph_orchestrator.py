#!/usr/bin/env python3
"""
LangGraph-Based Orchestrator

Replaces the custom orchestrator with a proper LangGraph StateGraph implementation
following LangGraph multi-agent best practices.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, Literal, List
from datetime import datetime

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool

from metadata_agent import MetadataAgent
from entitlement_agent import EntitlementAgent
from data_agent import DataAgent
from aggregation_agent import AggregationAgent
from base_agent import BaseAgent

logger = logging.getLogger(__name__)

class DataflowState(MessagesState):
    """Enhanced state management following LangGraph patterns"""
    
    # Core request information
    task_description: str
    user_email: str
    session_id: str
    query: Optional[str] = None
    
    # Agent execution results
    metadata_results: Optional[Dict[str, Any]] = None
    entitlement_results: Optional[Dict[str, Any]] = None
    data_results: Optional[Dict[str, Any]] = None
    aggregation_results: Optional[Dict[str, Any]] = None
    
    # Workflow control
    current_agent: Optional[str] = None
    workflow_status: str = "started"
    error_count: int = 0
    max_errors: int = 3
    
    # Execution metadata
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    total_agents_executed: int = 0

class LangGraphOrchestrator:
    """LangGraph-based orchestrator following multi-agent best practices"""
    
    def __init__(self):
        # Initialize agents
        self.metadata_agent = MetadataAgent()
        self.entitlement_agent = EntitlementAgent()
        self.data_agent = DataAgent()
        self.aggregation_agent = AggregationAgent()
        
        # Build the state graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph StateGraph with proper agent handoffs"""
        
        # Create the state graph
        builder = StateGraph(DataflowState)
        
        # Add agent nodes
        builder.add_node("supervisor", self._supervisor_agent)
        builder.add_node("metadata_agent", self._metadata_agent_node)
        builder.add_node("entitlement_agent", self._entitlement_agent_node)
        builder.add_node("data_agent", self._data_agent_node)
        builder.add_node("aggregation_agent", self._aggregation_agent_node)
        builder.add_node("error_handler", self._error_handler_node)
        
        # Define the workflow
        builder.add_edge(START, "supervisor")
        
        # All agents return to supervisor for coordination
        builder.add_edge("metadata_agent", "supervisor")
        builder.add_edge("entitlement_agent", "supervisor") 
        builder.add_edge("data_agent", "supervisor")
        builder.add_edge("aggregation_agent", "supervisor")
        builder.add_edge("error_handler", "supervisor")
        
        return builder.compile()
    
    async def _supervisor_agent(self, state: DataflowState) -> Command[Literal["metadata_agent", "entitlement_agent", "data_agent", "aggregation_agent", "error_handler", END]]:
        """
        Supervisor agent that coordinates the workflow using LLM reasoning
        Following LangGraph supervisor pattern
        """
        
        # Check for errors
        if state.error_count >= state.max_errors:
            logger.error(f"Max errors ({state.max_errors}) reached, terminating workflow")
            return Command(
                goto=END,
                update={
                    "workflow_status": "failed",
                    "completed_at": datetime.now().isoformat()
                }
            )
        
        # Use LLM to decide next step based on current state
        next_agent = await self._llm_decide_next_agent(state)
        
        if next_agent == "complete":
            return Command(
                goto=END,
                update={
                    "workflow_status": "completed",
                    "completed_at": datetime.now().isoformat()
                }
            )
        elif next_agent == "error":
            return Command(goto="error_handler")
        else:
            return Command(
                goto=next_agent,
                update={"current_agent": next_agent}
            )
    
    async def _llm_decide_next_agent(self, state: DataflowState) -> str:
        """Use LLM to intelligently decide the next agent to execute"""
        
        # Create system prompt for supervisor decision-making
        system_prompt = """
        You are a workflow supervisor coordinating a multi-agent data analysis system.
        
        Available agents:
        - metadata_agent: Discovers data schemas and structures
        - entitlement_agent: Validates security and access permissions  
        - data_agent: Retrieves and processes data from sources
        - aggregation_agent: Analyzes and synthesizes results
        
        Workflow rules:
        1. Metadata discovery should typically happen first
        2. Entitlement validation should happen before data access
        3. Data retrieval should happen after entitlement approval
        4. Aggregation should happen after data retrieval
        5. Some agents can run in parallel if appropriate
        
        Decide which agent should execute next based on current state.
        """
        
        # Analyze current state
        state_summary = {
            "task": state.task_description,
            "metadata_completed": state.metadata_results is not None,
            "entitlement_completed": state.entitlement_results is not None,
            "data_completed": state.data_results is not None,
            "aggregation_completed": state.aggregation_results is not None,
            "current_agent": state.current_agent,
            "error_count": state.error_count
        }
        
        user_prompt = f"""
        Current workflow state: {json.dumps(state_summary, indent=2)}
        
        Decide the next agent to execute. Options:
        - "metadata_agent" - if metadata discovery is needed
        - "entitlement_agent" - if security validation is needed
        - "data_agent" - if data retrieval is needed  
        - "aggregation_agent" - if final analysis is needed
        - "complete" - if all work is done
        - "error" - if there's an error condition
        
        Respond with just the agent name.
        """
        
        try:
            # Use the base agent's LLM calling capability
            llm_response = await self.metadata_agent.call_llm(system_prompt, user_prompt, max_tokens=50)
            
            # Extract decision
            decision = llm_response.strip().lower()
            
            # Validate decision
            valid_options = ["metadata_agent", "entitlement_agent", "data_agent", "aggregation_agent", "complete", "error"]
            if decision in valid_options:
                return decision
            else:
                logger.warning(f"Invalid LLM decision: {decision}, falling back to sequential logic")
                return self._fallback_decision_logic(state)
                
        except Exception as e:
            logger.error(f"LLM supervisor decision failed: {e}")
            return self._fallback_decision_logic(state)
    
    def _fallback_decision_logic(self, state: DataflowState) -> str:
        """Fallback decision logic when LLM fails"""
        
        if state.metadata_results is None:
            return "metadata_agent"
        elif state.entitlement_results is None:
            return "entitlement_agent"
        elif state.data_results is None:
            return "data_agent"
        elif state.aggregation_results is None:
            return "aggregation_agent"
        else:
            return "complete"
    
    async def _metadata_agent_node(self, state: DataflowState) -> Command[Literal["supervisor"]]:
        """Execute metadata agent with proper LangGraph integration"""
        
        try:
            logger.info("Executing metadata agent")
            
            # Convert state to context for agent
            context = self._state_to_context(state)
            
            # Execute agent
            result = await self.metadata_agent.execute(state.task_description, context)
            
            # Create agent message
            agent_message = AIMessage(
                content=f"Metadata discovery completed. Found {result.get('metadata_summary', {}).get('schemas_discovered', 0)} schemas.",
                name="metadata_agent"
            )
            
            return Command(
                goto="supervisor",
                update={
                    "metadata_results": result,
                    "messages": [agent_message],
                    "total_agents_executed": state.total_agents_executed + 1
                }
            )
            
        except Exception as e:
            logger.error(f"Metadata agent failed: {e}")
            return Command(
                goto="supervisor",
                update={
                    "error_count": state.error_count + 1,
                    "messages": [AIMessage(content=f"Metadata agent failed: {str(e)}", name="metadata_agent")]
                }
            )
    
    async def _entitlement_agent_node(self, state: DataflowState) -> Command[Literal["supervisor"]]:
        """Execute entitlement agent with proper LangGraph integration"""
        
        try:
            logger.info("Executing entitlement agent")
            
            # Convert state to context for agent
            context = self._state_to_context(state)
            
            # Execute agent
            result = await self.entitlement_agent.execute(state.task_description, context)
            
            # Create agent message
            access_granted = result.get("entitlement_summary", {}).get("access_granted", False)
            agent_message = AIMessage(
                content=f"Security validation completed. Access {'granted' if access_granted else 'denied'}.",
                name="entitlement_agent"
            )
            
            return Command(
                goto="supervisor",
                update={
                    "entitlement_results": result,
                    "messages": [agent_message],
                    "total_agents_executed": state.total_agents_executed + 1
                }
            )
            
        except Exception as e:
            logger.error(f"Entitlement agent failed: {e}")
            return Command(
                goto="supervisor",
                update={
                    "error_count": state.error_count + 1,
                    "messages": [AIMessage(content=f"Entitlement agent failed: {str(e)}", name="entitlement_agent")]
                }
            )
    
    async def _data_agent_node(self, state: DataflowState) -> Command[Literal["supervisor"]]:
        """Execute data agent with proper LangGraph integration"""
        
        try:
            logger.info("Executing data agent")
            
            # Check entitlement first
            if state.entitlement_results:
                access_granted = state.entitlement_results.get("entitlement_summary", {}).get("access_granted", False)
                if not access_granted:
                    logger.warning("Access denied by entitlement agent, skipping data retrieval")
                    return Command(
                        goto="supervisor",
                        update={
                            "data_results": {"error": "Access denied by entitlement validation"},
                            "messages": [AIMessage(content="Data access denied due to security restrictions", name="data_agent")]
                        }
                    )
            
            # Convert state to context for agent
            context = self._state_to_context(state)
            
            # Execute agent
            result = await self.data_agent.execute(state.task_description, context)
            
            # Create agent message
            tools_executed = len(result.get("tool_execution_results", []))
            agent_message = AIMessage(
                content=f"Data retrieval completed. Executed {tools_executed} data tools.",
                name="data_agent"
            )
            
            return Command(
                goto="supervisor",
                update={
                    "data_results": result,
                    "messages": [agent_message],
                    "total_agents_executed": state.total_agents_executed + 1
                }
            )
            
        except Exception as e:
            logger.error(f"Data agent failed: {e}")
            return Command(
                goto="supervisor",
                update={
                    "error_count": state.error_count + 1,
                    "messages": [AIMessage(content=f"Data agent failed: {str(e)}", name="data_agent")]
                }
            )
    
    async def _aggregation_agent_node(self, state: DataflowState) -> Command[Literal["supervisor"]]:
        """Execute aggregation agent with proper LangGraph integration"""
        
        try:
            logger.info("Executing aggregation agent")
            
            # Convert state to context for agent
            context = self._state_to_context(state)
            
            # Execute agent
            result = await self.aggregation_agent.execute(state.task_description, context)
            
            # Create agent message
            insights_count = len(result.get("final_synthesis", {}).get("primary_insights", []))
            agent_message = AIMessage(
                content=f"Analysis completed. Generated {insights_count} key insights.",
                name="aggregation_agent"
            )
            
            return Command(
                goto="supervisor",
                update={
                    "aggregation_results": result,
                    "messages": [agent_message],
                    "total_agents_executed": state.total_agents_executed + 1
                }
            )
            
        except Exception as e:
            logger.error(f"Aggregation agent failed: {e}")
            return Command(
                goto="supervisor",
                update={
                    "error_count": state.error_count + 1,
                    "messages": [AIMessage(content=f"Aggregation agent failed: {str(e)}", name="aggregation_agent")]
                }
            )
    
    async def _error_handler_node(self, state: DataflowState) -> Command[Literal["supervisor"]]:
        """Handle errors and attempt recovery"""
        
        logger.info(f"Handling error (count: {state.error_count})")
        
        # Add error handling message
        error_message = AIMessage(
            content=f"Error handled. Attempting recovery (error count: {state.error_count})",
            name="error_handler"
        )
        
        return Command(
            goto="supervisor",
            update={
                "messages": [error_message],
                "workflow_status": "recovering"
            }
        )
    
    def _state_to_context(self, state: DataflowState) -> Dict[str, Any]:
        """Convert LangGraph state to agent context format"""
        return {
            "user_email": state.user_email,
            "session_id": state.session_id,
            "query": state.query,
            "metadata_results": state.metadata_results,
            "entitlement_results": state.entitlement_results,
            "data_results": state.data_results,
            "workflow_status": state.workflow_status,
            "messages": state.messages
        }
    
    async def process_request(self, task_description: str, user_email: str, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a data analysis request using LangGraph workflow
        
        Args:
            task_description: The data analysis task to perform
            user_email: User making the request
            query: Optional specific query
            
        Returns:
            Complete workflow results
        """
        
        # Create initial state
        initial_state = DataflowState(
            messages=[HumanMessage(content=task_description)],
            task_description=task_description,
            user_email=user_email,
            session_id=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            query=query,
            started_at=datetime.now().isoformat()
        )
        
        try:
            # Execute the workflow
            logger.info(f"Starting LangGraph workflow for task: {task_description}")
            final_state = await self.graph.ainvoke(initial_state)
            
            # Return comprehensive results
            return {
                "workflow_status": final_state.get("workflow_status", "completed"),
                "metadata_results": final_state.get("metadata_results"),
                "entitlement_results": final_state.get("entitlement_results"),
                "data_results": final_state.get("data_results"),
                "aggregation_results": final_state.get("aggregation_results"),
                "execution_summary": {
                    "total_agents_executed": final_state.get("total_agents_executed", 0),
                    "error_count": final_state.get("error_count", 0),
                    "started_at": final_state.get("started_at"),
                    "completed_at": final_state.get("completed_at"),
                    "session_id": final_state.get("session_id")
                },
                "messages": final_state.get("messages", []),
                "success": final_state.get("workflow_status") == "completed"
            }
            
        except Exception as e:
            logger.error(f"LangGraph workflow failed: {e}")
            return {
                "workflow_status": "failed",
                "error": str(e),
                "success": False
            }

# Alternative: Tool-calling Supervisor Pattern
# This follows LangGraph's supervisor (tool-calling) pattern where agents are tools

@tool
def execute_metadata_discovery(task_description: str, context: str) -> Command:
    """Execute metadata discovery for data schema analysis."""
    return Command(
        goto="metadata_agent",
        update={"task_description": task_description, "tool_context": context}
    )

@tool  
def execute_entitlement_validation(security_context: str) -> Command:
    """Execute security and entitlement validation."""
    return Command(
        goto="entitlement_agent",
        update={"security_context": security_context}
    )

@tool
def execute_data_retrieval(data_context: str) -> Command:
    """Execute data retrieval from configured sources."""
    return Command(
        goto="data_agent", 
        update={"data_context": data_context}
    )

@tool
def execute_aggregation_analysis(analysis_context: str) -> Command:
    """Execute final aggregation and analysis."""
    return Command(
        goto="aggregation_agent",
        update={"analysis_context": analysis_context}
    )

class ToolCallingSupervisorOrchestrator:
    """Alternative implementation using LangGraph's tool-calling supervisor pattern"""
    
    def __init__(self):
        self.tools = [
            execute_metadata_discovery,
            execute_entitlement_validation, 
            execute_data_retrieval,
            execute_aggregation_analysis
        ]
        # Implementation would use ToolNode and tool-calling LLM
        # See LangGraph documentation for complete example 
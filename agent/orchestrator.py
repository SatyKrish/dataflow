#!/usr/bin/env python3
"""
LangGraph Multi-Agent Orchestrator

Modern LangGraph StateGraph implementation for intelligent multi-agent coordination
with LLM-powered workflow supervision and Command-based handoffs.
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
from azure_openai_client import LLMValidationError

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

class Orchestrator:
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
            # Use the base agent's improved LLM calling capability
            llm_response = await self.metadata_agent.call_llm(system_prompt, user_prompt, max_tokens=50)
            
            # Extract decision
            decision = llm_response.strip().lower()
            
            # Validate decision
            valid_options = ["metadata_agent", "entitlement_agent", "data_agent", "aggregation_agent", "complete", "error"]
            if decision in valid_options:
                logger.info(f"LLM supervisor decided: {decision}")
                return decision
            else:
                logger.warning(f"Invalid LLM decision: {decision}, falling back to sequential logic")
                return self._fallback_decision_logic(state)
                
        except LLMValidationError as e:
            logger.error(f"Azure OpenAI validation error in supervisor decision: {e}")
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
        """Execute metadata agent with proper state management"""
        
        logger.info("Executing metadata agent")
        
        try:
            # Create context from current state
            context = self._state_to_context(state)
            
            # Execute the agent
            result = await self.metadata_agent.execute(
                session_id=state.session_id,
                task_description=f"Metadata discovery: {state.task_description}",
                context=context
            )
            
            # Add message to conversation
            metadata_message = AIMessage(
                content=f"Metadata Agent completed: {result.get('summary', 'Metadata discovery executed')}",
                name="metadata_agent"
            )
            
            return Command(
                goto="supervisor",
                update={
                    "metadata_results": result,
                    "total_agents_executed": state.total_agents_executed + 1,
                    "messages": state.messages + [metadata_message]
                }
            )
            
        except Exception as e:
            logger.error(f"Metadata agent execution failed: {e}")
            error_message = AIMessage(
                content=f"Metadata Agent failed: {str(e)}",
                name="metadata_agent"
            )
            
            return Command(
                goto="supervisor",
                update={
                    "error_count": state.error_count + 1,
                    "messages": state.messages + [error_message]
                }
            )
    
    async def _entitlement_agent_node(self, state: DataflowState) -> Command[Literal["supervisor"]]:
        """Execute entitlement agent with proper state management"""
        
        logger.info("Executing entitlement agent")
        
        try:
            # Create context from current state
            context = self._state_to_context(state)
            
            # Execute the agent
            result = await self.entitlement_agent.execute(
                session_id=state.session_id,
                task_description=f"Entitlement validation: {state.task_description}",
                context=context
            )
            
            # Add message to conversation
            entitlement_message = AIMessage(
                content=f"Entitlement Agent completed: {result.get('summary', 'Entitlement validation executed')}",
                name="entitlement_agent"
            )
            
            return Command(
                goto="supervisor",
                update={
                    "entitlement_results": result,
                    "total_agents_executed": state.total_agents_executed + 1,
                    "messages": state.messages + [entitlement_message]
                }
            )
            
        except Exception as e:
            logger.error(f"Entitlement agent execution failed: {e}")
            error_message = AIMessage(
                content=f"Entitlement Agent failed: {str(e)}",
                name="entitlement_agent"
            )
            
            return Command(
                goto="supervisor",
                update={
                    "error_count": state.error_count + 1,
                    "messages": state.messages + [error_message]
                }
            )
    
    async def _data_agent_node(self, state: DataflowState) -> Command[Literal["supervisor"]]:
        """Execute data agent with proper state management"""
        
        logger.info("Executing data agent")
        
        try:
            # Create context from current state including metadata and entitlement
            context = self._state_to_context(state)
            
            # Execute the agent
            result = await self.data_agent.execute(
                session_id=state.session_id,
                task_description=f"Data retrieval: {state.task_description}",
                context=context
            )
            
            # Add message to conversation
            data_message = AIMessage(
                content=f"Data Agent completed: {result.get('summary', 'Data retrieval executed')}",
                name="data_agent"
            )
            
            return Command(
                goto="supervisor",
                update={
                    "data_results": result,
                    "total_agents_executed": state.total_agents_executed + 1,
                    "messages": state.messages + [data_message]
                }
            )
            
        except Exception as e:
            logger.error(f"Data agent execution failed: {e}")
            error_message = AIMessage(
                content=f"Data Agent failed: {str(e)}",
                name="data_agent"
            )
            
            return Command(
                goto="supervisor",
                update={
                    "error_count": state.error_count + 1,
                    "messages": state.messages + [error_message]
                }
            )
    
    async def _aggregation_agent_node(self, state: DataflowState) -> Command[Literal["supervisor"]]:
        """Execute aggregation agent with proper state management"""
        
        logger.info("Executing aggregation agent")
        
        try:
            # Create context from all previous results
            context = self._state_to_context(state)
            
            # Execute the agent
            result = await self.aggregation_agent.execute(
                session_id=state.session_id,
                task_description=f"Analysis synthesis: {state.task_description}",
                context=context
            )
            
            # Add message to conversation
            aggregation_message = AIMessage(
                content=f"Aggregation Agent completed: {result.get('summary', 'Analysis synthesis executed')}",
                name="aggregation_agent"
            )
            
            return Command(
                goto="supervisor",
                update={
                    "aggregation_results": result,
                    "total_agents_executed": state.total_agents_executed + 1,
                    "messages": state.messages + [aggregation_message]
                }
            )
            
        except Exception as e:
            logger.error(f"Aggregation agent execution failed: {e}")
            error_message = AIMessage(
                content=f"Aggregation Agent failed: {str(e)}",
                name="aggregation_agent"
            )
            
            return Command(
                goto="supervisor",
                update={
                    "error_count": state.error_count + 1,
                    "messages": state.messages + [error_message]
                }
            )
    
    async def _error_handler_node(self, state: DataflowState) -> Command[Literal["supervisor"]]:
        """Handle errors and recovery"""
        
        logger.warning("Error handler activated")
        
        error_message = AIMessage(
            content="Error handler activated - attempting recovery",
            name="error_handler"
        )
        
        return Command(
            goto="supervisor", 
            update={
                "messages": state.messages + [error_message]
            }
        )
    
    def _state_to_context(self, state: DataflowState) -> Dict[str, Any]:
        """Convert state to context dict for agent execution"""
        return {
            "metadata_results": state.metadata_results,
            "entitlement_results": state.entitlement_results, 
            "data_results": state.data_results,
            "user_email": state.user_email,
            "query": state.query
        }
    
    async def process_request(self, task_description: str, user_email: str, query: Optional[str] = None) -> Dict[str, Any]:
        """
        Main entry point for processing research requests
        
        Args:
            task_description: The research task to execute
            user_email: User making the request
            query: Optional specific query
            
        Returns:
            Dict containing complete results and metadata
        """
        
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create initial state
        initial_state = DataflowState(
            messages=[HumanMessage(content=task_description)],
            task_description=task_description,
            user_email=user_email,
            session_id=session_id,
            query=query,
            started_at=datetime.now().isoformat()
        )
        
        logger.info(f"Processing request: {task_description[:100]}...")
        
        try:
            # Execute the graph
            final_state = await self.graph.ainvoke(initial_state)
            
            # Compile comprehensive results
            results = {
                "session_id": final_state["session_id"],
                "task_description": final_state["task_description"],
                "user_email": final_state["user_email"],
                "workflow_status": final_state["workflow_status"],
                "started_at": final_state["started_at"],
                "completed_at": final_state.get("completed_at"),
                "total_agents_executed": final_state["total_agents_executed"],
                "error_count": final_state["error_count"],
                
                # Agent results
                "metadata_results": final_state.get("metadata_results"),
                "entitlement_results": final_state.get("entitlement_results"),
                "data_results": final_state.get("data_results"),
                "aggregation_results": final_state.get("aggregation_results"),
                
                # Conversation history
                "messages": [
                    {
                        "type": type(msg).__name__,
                        "content": msg.content,
                        "name": getattr(msg, 'name', None)
                    }
                    for msg in final_state["messages"]
                ]
            }
            
            logger.info(f"Request completed successfully: {session_id}")
            return results
            
        except Exception as e:
            logger.error(f"Request processing failed: {e}")
            return {
                "session_id": session_id,
                "task_description": task_description,
                "user_email": user_email,
                "workflow_status": "failed",
                "started_at": initial_state.started_at,
                "completed_at": datetime.now().isoformat(),
                "error": str(e),
                "error_count": 1
            }

# Tool definitions for potential tool-calling supervisor pattern
@tool
def execute_metadata_discovery(task_description: str, context: str) -> Command:
    """Execute metadata discovery for the given task"""
    return Command(goto="metadata_agent")

@tool  
def execute_entitlement_validation(security_context: str) -> Command:
    """Execute entitlement validation for security compliance"""
    return Command(goto="entitlement_agent")

@tool
def execute_data_retrieval(data_context: str) -> Command:
    """Execute data retrieval from configured sources"""
    return Command(goto="data_agent")

@tool
def execute_aggregation_analysis(analysis_context: str) -> Command:
    """Execute final aggregation and analysis"""
    return Command(goto="aggregation_agent")

class ToolCallingSupervisorOrchestrator:
    """Alternative implementation using tool-calling supervisor pattern"""
    
    def __init__(self):
        # This would implement tool-calling based coordination
        # keeping for future consideration if needed
        pass 
-- Multi-Agent Research System Database Schema
-- PostgreSQL schema for MVP implementation

-- Extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text similarity searches

-- Basic user management for MVP
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Research sessions for multi-agent orchestration
CREATE TABLE research_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id),
    initial_query TEXT NOT NULL,
    research_plan JSONB,
    final_outcome JSONB,
    token_usage INTEGER DEFAULT 0,
    session_duration INTERVAL,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'failed', 'cancelled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Subagent execution tracking
CREATE TABLE subagent_executions (
    execution_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES research_sessions(session_id),
    agent_type VARCHAR(50) NOT NULL CHECK (agent_type IN ('metadata', 'entitlement', 'data', 'aggregation')),
    task_description TEXT,
    tool_calls JSONB,
    results JSONB,
    status VARCHAR(50) DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed')),
    execution_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Session memory for context management
CREATE TABLE session_memory (
    memory_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES research_sessions(session_id),
    memory_type VARCHAR(50) NOT NULL CHECK (memory_type IN ('research_plan', 'intermediate_results', 'context_summary', 'artifact_reference')),
    content JSONB,
    artifact_path TEXT, -- For large files stored on filesystem
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Agent performance metrics
CREATE TABLE agent_metrics (
    metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES research_sessions(session_id),
    agent_type VARCHAR(50),
    metric_name VARCHAR(100),
    metric_value NUMERIC,
    metric_unit VARCHAR(50),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_research_sessions_user_id ON research_sessions(user_id);
CREATE INDEX idx_research_sessions_status ON research_sessions(status);
CREATE INDEX idx_research_sessions_created_at ON research_sessions(created_at);

CREATE INDEX idx_subagent_executions_session_id ON subagent_executions(session_id);
CREATE INDEX idx_subagent_executions_agent_type ON subagent_executions(agent_type);
CREATE INDEX idx_subagent_executions_status ON subagent_executions(status);
CREATE INDEX idx_subagent_executions_created_at ON subagent_executions(created_at);

CREATE INDEX idx_session_memory_session_id ON session_memory(session_id);
CREATE INDEX idx_session_memory_type ON session_memory(memory_type);
CREATE INDEX idx_session_memory_expires_at ON session_memory(expires_at);

-- GIN indexes for JSONB fields
CREATE INDEX idx_research_sessions_plan_gin ON research_sessions USING GIN (research_plan);
CREATE INDEX idx_research_sessions_outcome_gin ON research_sessions USING GIN (final_outcome);
CREATE INDEX idx_subagent_executions_results_gin ON subagent_executions USING GIN (results);
CREATE INDEX idx_session_memory_content_gin ON session_memory USING GIN (content);

-- Full-text search indexes
CREATE INDEX idx_research_sessions_query_fulltext ON research_sessions USING GIN (to_tsvector('english', initial_query));
CREATE INDEX idx_subagent_executions_task_fulltext ON subagent_executions USING GIN (to_tsvector('english', task_description)); 
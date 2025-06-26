/**
 * MCP types aligned with the official SDK
 * Import and extend the official types rather than redefining them
 */

import type { 
  Tool as SDKTool,
  Resource as SDKResource, 
  Prompt as SDKPrompt,
  CallToolResult as SDKCallToolResult,
  ListToolsResult,
  ListResourcesResult,
  ListPromptsResult,
  CallToolRequest
} from '@modelcontextprotocol/sdk/types.js'

// Use SDK types directly or extend them minimally
export type MCPTool = SDKTool
export type MCPResource = SDKResource  
export type MCPPrompt = SDKPrompt
export type MCPToolResult = SDKCallToolResult

// SDK request/response types
export type MCPListToolsResult = ListToolsResult
export type MCPListResourcesResult = ListResourcesResult
export type MCPListPromptsResult = ListPromptsResult
export type MCPCallToolRequest = CallToolRequest

// Only define custom types for application-specific needs
export interface MCPClientStatus {
  connected: boolean;
  serverName: string;
  tools: MCPTool[];
  resources: MCPResource[];
  prompts: MCPPrompt[];
  error?: string;
}

// Keep your existing config types as they're application-specific
export interface MCPConfig {
  inputs?: MCPInput[];
  servers: Record<string, MCPServerConfig>;
}

export interface MCPInput {
  type: 'promptString' | 'promptChoice';
  id: string;
  description: string;
  password?: boolean;
  choices?: string[];
}

export interface MCPServerConfig {
  type: 'stdio' | 'http';
  url?: string;
  command?: string;
  args?: string[];
  env?: Record<string, string>;
  headers?: Record<string, string>;
  description?: string;
  timeout?: number;
}

export interface MCPToolCall {
  name: string;
  arguments: Record<string, any>;
}

export interface AzureOpenAIConfig {
  endpoint: string;
  apiKey?: string;
  deploymentName: string;
  apiVersion?: string;
  useAzureAD?: boolean;
}

export interface MCPChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  toolCalls?: MCPToolCall[];
  toolResults?: MCPToolResult[];
}

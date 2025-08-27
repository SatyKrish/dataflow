import { LangGraphAdapter } from "../adapters/langgraph/LangGraphAdapter";
import type { AgentProvider } from "./types";
// Optional: your existing REST provider
// import { DiscoveryAgentHTTPProvider } from "@/agent/providers/DiscoveryAgentHTTPProvider";

export function createProviderFromEnv(): AgentProvider {
  const backend = (process.env.NEXT_PUBLIC_AGENT_BACKEND ?? "langgraph").toLowerCase();

  if (backend === "rest") {
    // Uncomment and configure for REST fallback:
    // const baseUrl = process.env.NEXT_PUBLIC_DISCOVERY_BASE_URL!;
    // return new DiscoveryAgentHTTPProvider(baseUrl);
    throw new Error("REST provider not implemented. Uncomment and configure if needed.");
  }

  if (backend === "langgraph") {
    const baseUrl = process.env.NEXT_PUBLIC_LANGGRAPH_BASE_URL ?? "http://localhost:2024";
    const graph = process.env.NEXT_PUBLIC_LANGGRAPH_GRAPH ?? "research";
    return new LangGraphAdapter({ baseUrl, graph });
  }

  throw new Error(`Unsupported backend: ${backend}`);
}

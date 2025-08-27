import { DiscoveryAgentBridgeProvider } from "./DiscoveryAgentBridgeProvider";
import { LangGraphAdapter } from "@/agent/adapters/langgraph/LangGraphAdapter";
// import { DiscoveryAgentHTTPProvider } from "@/providers/DiscoveryAgentHTTPProvider"; // old REST

export function createDiscoveryProviderFromEnv() {
  const backend = (process.env.NEXT_PUBLIC_AGENT_BACKEND ?? "langgraph").toLowerCase();

  if (backend === "langgraph") {
    const baseUrl = process.env.NEXT_PUBLIC_LANGGRAPH_BASE_URL ?? "http://localhost:2024";
  const graph = process.env.NEXT_PUBLIC_LANGGRAPH_GRAPH || "research";
    const agent = new LangGraphAdapter({ baseUrl, graph });
    return new DiscoveryAgentBridgeProvider(agent);
  }

  if (backend === "rest") {
    // return new DiscoveryAgentHTTPProvider(process.env.NEXT_PUBLIC_DISCOVERY_BASE_URL!);
  }

  throw new Error(`Unsupported backend: ${backend}. Set NEXT_PUBLIC_AGENT_BACKEND to 'langgraph' or 'rest'.`);
}

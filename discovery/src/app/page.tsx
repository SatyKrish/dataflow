"use client";


import * as React from "react";
import DiscoveryAgentUI from "@/components/discovery-agent/discovery-agent-ui";
import { AgentDiscoveryProvider } from "@/agent/core/AgentDiscoveryProvider";

export default function Page() {
  const provider = React.useMemo(() => new AgentDiscoveryProvider(), []);
  return <DiscoveryAgentUI provider={provider} />;
}

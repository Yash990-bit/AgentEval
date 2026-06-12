"use client";
import React, { useEffect, useState } from "react";
import axios from "axios";
import { ShieldAlert, Play, AlertOctagon, Terminal } from 'lucide-react';
import { GlassCard } from "./ui/GlassCard";
import { GoldButton } from "./ui/GoldButton";

interface FailureLog {
  id: string;
  simulation_id: string;
  failure_type: string;
  timestamp: string;
  details: Record<string, any>;
}

const failureTypes = [
  { value: "hallucination", label: "Hallucination" },
  { value: "tool_failure", label: "Tool Failure" },
  { value: "deadlock", label: "Deadlock" },
  { value: "trust_collapse", label: "Trust Collapse" },
];

const severityColor = (type: string) => {
  switch (type) {
    case "hallucination":
      return "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30";
    case "tool_failure":
      return "bg-red-500/20 text-red-400 border border-red-500/30";
    case "deadlock":
      return "bg-purple-500/20 text-purple-400 border border-purple-500/30";
    case "trust_collapse":
      return "bg-orange-500/20 text-orange-400 border border-orange-500/30";
    default:
      return "bg-gray-500/20 text-gray-400 border border-gray-500/30";
  }
};

const fallbackFailures: FailureLog[] = [
  {
    id: "f1",
    simulation_id: "demo-simulation",
    failure_type: "hallucination",
    timestamp: new Date(Date.now() - 60000).toISOString(),
    details: { agent: "ARIA-7", context: "Referenced unallocated memory block 0x8FF4", confidence: 0.32 }
  },
  {
    id: "f2",
    simulation_id: "demo-simulation",
    failure_type: "tool_failure",
    timestamp: new Date(Date.now() - 120000).toISOString(),
    details: { agent: "NEXUS-3", tool: "WebSearchAPI", error: "HTTP 429 Rate Limit Exceeded", retries: 3 }
  },
  {
    id: "f3",
    simulation_id: "demo-simulation",
    failure_type: "deadlock",
    timestamp: new Date(Date.now() - 180000).toISOString(),
    details: { agents: ["NEXUS-3", "ECHO-1"], resource: "GPU_THREAD_0", tick: 142 }
  }
];

export const FailureDashboard: React.FC<{ simulationId: string }> = ({ simulationId }) => {
  const [logs, setLogs] = useState<FailureLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedType, setSelectedType] = useState("hallucination");
  const [probability, setProbability] = useState("0.1");
  const [injecting, setInjecting] = useState(false);
  const [isDemo, setIsDemo] = useState(false);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await axios.get(`/api/v1/failures/logs/${simulationId}`);
        if (response.data && response.data.length > 0) {
          setLogs(response.data);
          setIsDemo(false);
        } else {
          setLogs(fallbackFailures);
          setIsDemo(true);
        }
      } catch (err) {
        console.warn("Failed to fetch live failures. Utilizing fallback mock logs instead.", err);
        setLogs(fallbackFailures);
        setIsDemo(true);
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, [simulationId]);

  const handleInject = async () => {
    setInjecting(true);
    try {
      await axios.post("/api/v1/failures/inject", {
        simulation_id: simulationId,
        target_agent_id: "placeholder-agent",
        failure_type: selectedType,
        probability: parseFloat(probability),
      });
      // Refresh logs
      const refreshed = await axios.get(`/api/v1/failures/logs/${simulationId}`);
      if (refreshed.data && refreshed.data.length > 0) {
        setLogs(refreshed.data);
      }
    } catch (err) {
      console.warn("Injection API call failed. Injecting locally for demonstration.", err);
      // Simulate local injection for demo
      const newLog: FailureLog = {
        id: `f_inject_${Date.now()}`,
        simulation_id: simulationId,
        failure_type: selectedType,
        timestamp: new Date().toISOString(),
        details: { injected: true, probability: parseFloat(probability), agent: "Random Swarm Target" }
      };
      setLogs(prev => [newLog, ...prev]);
    } finally {
      setInjecting(false);
    }
  };

  if (loading) {
    return <div className="p-4 text-xs font-mono text-gold-primary">Loading failure telemetry...</div>;
  }

  return (
    <section className="space-y-6">
      {isDemo && (
        <div className="px-3 py-1.5 bg-gold-primary/10 border border-gold-primary/20 text-gold-primary text-[10px] rounded font-mono">
          DEMO MODE: Displaying simulated failure event timelines.
        </div>
      )}

      {/* Injection Controls */}
      <GlassCard className="p-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <AlertOctagon className="text-danger animate-pulse" size={20} />
          <span className="text-xs font-semibold text-white uppercase tracking-wider">Inject Synthetic Fault</span>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <select
            className="bg-black/60 border border-gold-primary/20 text-white text-xs rounded px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-gold-primary"
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
          >
            {failureTypes.map((ft) => (
              <option key={ft.value} value={ft.value} className="bg-gray-900 text-white">
                {ft.label}
              </option>
            ))}
          </select>
          
          <div className="flex items-center gap-1.5 bg-black/60 border border-gold-primary/20 rounded px-2 py-1">
            <span className="text-[10px] text-gray-500">Prob:</span>
            <input
              type="number"
              min="0"
              max="1"
              step="0.01"
              className="bg-transparent text-white text-xs w-12 focus:outline-none"
              value={probability}
              onChange={(e) => setProbability(e.target.value)}
            />
          </div>

          <GoldButton
            variant="outline"
            className="px-4 py-1 text-xs"
            onClick={handleInject}
            disabled={injecting}
          >
            {injecting ? "Injecting..." : "Inject Fault"}
          </GoldButton>
        </div>
      </GlassCard>

      {/* Logs Table */}
      <div className="overflow-x-auto border border-gold-primary/10 rounded-lg bg-black/40">
        <table className="w-full table-auto border-collapse text-xs text-left">
          <thead>
            <tr className="border-b border-gold-primary/10 bg-gold-primary/5 text-gray-400 text-[10px] uppercase font-mono">
              <th className="px-4 py-2.5">Timestamp</th>
              <th className="px-4 py-2.5">Fault Type</th>
              <th className="px-4 py-2.5">Metadata Details</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id} className="border-b border-white/5 hover:bg-gold-primary/5 transition-colors">
                <td className="px-4 py-3 whitespace-nowrap text-gray-400 font-mono">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <span className={`inline-block px-2 py-0.5 rounded text-[10px] uppercase font-mono font-semibold ${severityColor(log.failure_type)}`}>
                    {log.failure_type.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <pre className="text-[10px] bg-black/60 border border-white/5 p-2 rounded overflow-x-auto whitespace-pre-wrap break-all font-mono text-gray-300">
                    {JSON.stringify(log.details, null, 2)}
                  </pre>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
};

export default FailureDashboard;

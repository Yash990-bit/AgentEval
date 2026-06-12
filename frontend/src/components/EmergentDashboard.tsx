"use client";
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Eye, ShieldCheck, Sparkles, Terminal } from 'lucide-react';
import { GlassCard } from "./ui/GlassCard";

interface EmergentEvent {
  id: string;
  simulation_id: string;
  event_type: string;
  details: string; // JSON string
  created_at: string;
}

const fallbackEmergent: EmergentEvent[] = [
  {
    id: "e1",
    simulation_id: "demo-simulation",
    event_type: "Altruistic Resource Sharing",
    details: JSON.stringify({ agent_donor: "ARIA-7", agent_receiver: "ECHO-1", shared_resource: "API_BUDGET", transfer_rate: 0.15, motivation: "ECHO-1 battery energy level dipped below 30% safety mark." }, null, 2),
    created_at: new Date(Date.now() - 45000).toISOString()
  },
  {
    id: "e2",
    simulation_id: "demo-simulation",
    event_type: "Sub-swarm Consensus Coalescence",
    details: JSON.stringify({ agents: ["ARIA-7", "NEXUS-3"], consensus_topic: "Search Path Optimization", iterations: 4, convergence_confidence: 0.96 }, null, 2),
    created_at: new Date(Date.now() - 95000).toISOString()
  }
];

export default function EmergentDashboard({ simulationId }: { simulationId: string }) {
  const [events, setEvents] = useState<EmergentEvent[]>([]);
  const [isDemo, setIsDemo] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const res = await axios.get<EmergentEvent[]>(`/api/v1/emergent/${simulationId}`);
        const data = res.data;
        if (data && data.length > 0) {
          setEvents(data);
          setIsDemo(false);
        } else {
          setEvents(fallbackEmergent);
          setIsDemo(true);
        }
      } catch (e) {
        console.warn("Could not fetch emergent events. Utilizing simulated mock consensus log.", e);
        setEvents(fallbackEmergent);
        setIsDemo(true);
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
    const interval = setInterval(fetchEvents, 8000); // refresh every 8s
    return () => clearInterval(interval);
  }, [simulationId]);

  if (loading) {
    return <div className="text-xs font-mono text-gold-primary">Loading emergent telemetry...</div>;
  }

  return (
    <div className="space-y-4">
      {isDemo && (
        <div className="px-3 py-1.5 bg-gold-primary/10 border border-gold-primary/20 text-gold-primary text-[10px] rounded font-mono">
          DEMO MODE: Monitoring emergent behaviors in background nodes.
        </div>
      )}

      {events.length === 0 ? (
        <p className="text-gray-500 italic text-xs">No emergent events recorded yet.</p>
      ) : (
        <ul className="space-y-4">
          {events.map((e) => (
            <li key={e.id} className="p-4 border border-gold-primary/10 rounded-lg bg-black/40 hover:border-gold-primary/30 transition-all">
              <div className="flex justify-between items-center text-xs font-semibold text-white mb-2 pb-2 border-b border-white/5">
                <span className="flex items-center gap-1.5 text-gold-primary">
                  <ShieldCheck size={14} />
                  {e.event_type}
                </span>
                <span className="text-[10px] text-gray-500 font-mono">
                  {new Date(e.created_at).toLocaleTimeString()}
                </span>
              </div>
              <pre className="bg-black/60 border border-white/5 p-3 rounded text-[10px] font-mono text-gray-300 overflow-x-auto whitespace-pre-wrap break-all leading-relaxed">
                {e.details}
              </pre>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

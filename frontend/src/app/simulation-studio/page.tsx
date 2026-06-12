"use client";
import React, { useState } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
  Edge,
  Node,
  BackgroundVariant,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip as ReTooltip,
  ResponsiveContainer,
} from 'recharts';
import { GlassCard } from '@/components/ui/GlassCard';
import { GoldButton } from '@/components/ui/GoldButton';
import { progressData as initialProgress } from '@/lib/mockData';
import FailureDashboard from '@/components/FailureDashboard';
import EmergentDashboard from '@/components/EmergentDashboard';
import PredictionPanel from '@/components/PredictionPanel';
import { Layers, AlertTriangle, Cpu, TrendingUp } from 'lucide-react';

export default function SimulationStudioPage() {
  const [nodes, setNodes] = useState<Node[]>([
    { id: '1', data: { label: 'ARIA-7' }, position: { x: 0, y: 0 } },
    { id: '2', data: { label: 'NEXUS-3' }, position: { x: 200, y: 0 } },
    { id: '3', data: { label: 'ECHO-1' }, position: { x: 100, y: 150 } },
  ]);
  const [edges, setEdges] = useState<Edge[]>([
    { id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: 'var(--gold-primary)' } },
    { id: 'e2-3', source: '2', target: '3', animated: true, style: { stroke: 'var(--gold-primary)' } },
    { id: 'e3-1', source: '3', target: '1', animated: true, style: { stroke: 'var(--gold-primary)' } },
  ]);
  const [isRunning, setIsRunning] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [progress, setProgress] = useState(initialProgress);
  
  // Tab controller: canvas, failures, emergence, predictions
  const [activeTab, setActiveTab] = useState<'canvas' | 'failures' | 'emergence' | 'predictions'>('canvas');

  // Update live progress dynamically when running
  React.useEffect(() => {
    if (!isRunning) return;
    const interval = setInterval(() => {
      setProgress(prev => {
        const last = prev[prev.length - 1];
        const nextTick = last ? last.tick + 1 : 0;
        const delta = Math.floor(Math.random() * 30) - 13; // random walk
        const nextAgents = Math.max(100, (last ? last.agents : 500) + delta);
        return [...prev.slice(1), { tick: nextTick, agents: nextAgents }];
      });
    }, 1000 / speed);
    return () => clearInterval(interval);
  }, [isRunning, speed]);

  const onConnect = (connection: any) =>
    setEdges((eds) => addEdge({ ...connection, animated: true, style: { stroke: 'var(--gold-primary)' } }, eds));

  // Dynamic styling based on running status
  const styledNodes = React.useMemo<Node[]>(() => {
    return nodes.map(n => ({
      ...n,
      style: {
        background: 'rgba(26, 26, 26, 0.9)',
        color: '#fff',
        border: isRunning ? '2px solid var(--gold-secondary)' : '1px solid rgba(212, 175, 55, 0.3)',
        boxShadow: isRunning ? '0 0 15px rgba(255, 215, 0, 0.4)' : 'none',
        borderRadius: '8px',
        padding: '10px',
        fontWeight: 'bold',
        transition: 'all 0.3s ease',
      }
    }));
  }, [nodes, isRunning]);

  const styledEdges = React.useMemo<Edge[]>(() => {
    return edges.map(e => ({
      ...e,
      animated: isRunning,
      style: {
        stroke: isRunning ? 'var(--gold-secondary)' : 'rgba(212, 175, 55, 0.3)',
        strokeWidth: isRunning ? 2 : 1,
        transition: 'all 0.3s ease',
      }
    }));
  }, [edges, isRunning]);

  return (
    <div className="p-8 space-y-6">
      {/* Sub navigation Tabs */}
      <div className="flex gap-2 border-b border-gold-primary/10 pb-3">
        <button
          onClick={() => setActiveTab('canvas')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all border ${
            activeTab === 'canvas'
              ? 'bg-gold-primary text-black border-gold-secondary font-bold shadow-[0_0_10px_rgba(212,175,55,0.3)]'
              : 'bg-black/40 border-gold-primary/10 text-gray-400 hover:text-white hover:bg-gold-primary/5'
          }`}
        >
          <Layers size={14} />
          Design Canvas
        </button>

        <button
          onClick={() => setActiveTab('failures')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all border ${
            activeTab === 'failures'
              ? 'bg-gold-primary text-black border-gold-secondary font-bold shadow-[0_0_10px_rgba(212,175,55,0.3)]'
              : 'bg-black/40 border-gold-primary/10 text-gray-400 hover:text-white hover:bg-gold-primary/5'
          }`}
        >
          <AlertTriangle size={14} />
          Failure Telemetry
        </button>

        <button
          onClick={() => setActiveTab('emergence')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all border ${
            activeTab === 'emergence'
              ? 'bg-gold-primary text-black border-gold-secondary font-bold shadow-[0_0_10px_rgba(212,175,55,0.3)]'
              : 'bg-black/40 border-gold-primary/10 text-gray-400 hover:text-white hover:bg-gold-primary/5'
          }`}
        >
          <Cpu size={14} />
          Emergent Swarm Logs
        </button>

        <button
          onClick={() => setActiveTab('predictions')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all border ${
            activeTab === 'predictions'
              ? 'bg-gold-primary text-black border-gold-secondary font-bold shadow-[0_0_10px_rgba(212,175,55,0.3)]'
              : 'bg-black/40 border-gold-primary/10 text-gray-400 hover:text-white hover:bg-gold-primary/5'
          }`}
        >
          <TrendingUp size={14} />
          Predictive Diagnostics
        </button>
      </div>

      {activeTab === 'canvas' && (
        <GlassCard className="h-[600px] flex">
          {/* Canvas */}
          <div className="flex-1 mr-4">
            <ReactFlow
              nodes={styledNodes}
              edges={styledEdges}
              onNodesChange={(changes) => setNodes((nds) => applyNodeChanges(changes, nds) as Node[])}
              onEdgesChange={(changes) => setEdges((eds) => applyEdgeChanges(changes, eds) as Edge[])}
              onConnect={onConnect}
              fitView
              style={{ background: 'transparent' }}
            >
              <Background variant={BackgroundVariant.Dots} gap={12} size={1} color="var(--gold-primary)" />
              <Controls />
              <MiniMap nodeColor={() => 'var(--gold-primary)'} />
            </ReactFlow>
          </div>
          {/* Controls */}
          <div className="w-64 flex flex-col gap-4">
            <h4 className="text-lg font-semibold text-gold-primary">Simulation Controls</h4>
            <GoldButton variant="primary" onClick={() => setIsRunning(!isRunning)}>
              {isRunning ? 'Pause' : 'Play'}
            </GoldButton>
            <label className="text-sm text-gray-300">Speed</label>
            <input
              type="range"
              min={0.5}
              max={2}
              step={0.1}
              value={speed}
              onChange={(e) => setSpeed(parseFloat(e.target.value))}
              className="w-full cursor-pointer accent-gold-primary"
            />
            <span className="text-xs text-gray-400">{speed}x</span>
            <h4 className="text-lg font-semibold text-gold-primary mt-2">Live Progress</h4>
            <div className="h-60 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={progress}>
                  <defs>
                    <linearGradient id="colorProgress" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--gold-primary)" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="var(--gold-primary)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="tick" stroke="var(--gold-primary)" />
                  <YAxis stroke="var(--gold-primary)" />
                  <ReTooltip contentStyle={{ backgroundColor: 'rgba(26,26,26,0.9)', border: 'none', color: '#fff' }} />
                  <Area type="monotone" dataKey="agents" stroke="var(--gold-primary)" fill="url(#colorProgress)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </GlassCard>
      )}

      {activeTab === 'failures' && (
        <GlassCard className="p-6">
          <h3 className="text-xl font-bold mb-4 text-gold-primary">Failure Injection & Logs</h3>
          <FailureDashboard simulationId="demo-simulation" />
        </GlassCard>
      )}

      {activeTab === 'emergence' && (
        <GlassCard className="p-6">
          <h3 className="text-xl font-bold mb-4 text-gold-primary">Emergent Swarm Events</h3>
          <EmergentDashboard simulationId="demo-simulation" />
        </GlassCard>
      )}

      {activeTab === 'predictions' && (
        <GlassCard className="p-6">
          <h3 className="text-xl font-bold mb-4 text-gold-primary">Predictive Swarm Analytics</h3>
          <PredictionPanel simulationId="00000000-0000-0000-0000-000000000001" />
        </GlassCard>
      )}
    </div>
  );
}

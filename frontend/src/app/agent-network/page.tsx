"use client";
import React, { useState } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  applyNodeChanges,
  applyEdgeChanges,
  Node,
  Edge,
  BackgroundVariant,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { GlassCard } from '@/components/ui/GlassCard';

export default function AgentNetworkPage() {
  const initialNodes: Node[] = [
    { id: '1', data: { label: 'ARIA-7' }, position: { x: 0, y: 0 } },
    { id: '2', data: { label: 'NEXUS-3' }, position: { x: 250, y: 0 } },
    { id: '3', data: { label: 'ECHO-1' }, position: { x: 125, y: 150 } },
  ];

  const initialEdges: Edge[] = [
    { id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: 'var(--gold-primary)' } },
    { id: 'e2-3', source: '2', target: '3', animated: true, style: { stroke: 'var(--gold-primary)' } },
    { id: 'e3-1', source: '3', target: '1', animated: true, style: { stroke: 'var(--gold-primary)' } },
  ];

  const [nodes, setNodes] = useState<Node[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>(initialEdges);

  const styledNodes = React.useMemo<Node[]>(() => {
    return nodes.map(n => ({
      ...n,
      style: {
        background: 'rgba(26, 26, 26, 0.95)',
        color: '#fff',
        border: '1px solid rgba(212, 175, 55, 0.4)',
        boxShadow: '0 0 12px rgba(212, 175, 55, 0.15)',
        borderRadius: '8px',
        padding: '10px',
        fontWeight: 'bold',
        textAlign: 'center',
        minWidth: '100px',
      }
    }));
  }, [nodes]);

  const styledEdges = React.useMemo<Edge[]>(() => {
    return edges.map(e => ({
      ...e,
      style: {
        stroke: 'var(--gold-primary)',
        strokeWidth: 2,
      }
    }));
  }, [edges]);

  return (
    <div className="p-8">
      <GlassCard className="h-[600px] flex flex-col">
        <h3 className="text-2xl font-bold mb-4 text-gold-primary">Agent Network</h3>
        <div className="flex-1 min-h-0">
          <ReactFlow
            nodes={styledNodes}
            edges={styledEdges}
            onNodesChange={(changes) => setNodes((nds) => applyNodeChanges(changes, nds) as Node[])}
            onEdgesChange={(changes) => setEdges((eds) => applyEdgeChanges(changes, eds) as Edge[])}
            fitView
            style={{ background: 'transparent' }}
          >
            <Background variant={BackgroundVariant.Dots} gap={12} size={1} color="var(--gold-primary)" />
            <Controls />
            <MiniMap nodeColor={() => 'var(--gold-primary)'} />
          </ReactFlow>
        </div>
      </GlassCard>
    </div>
  );
}

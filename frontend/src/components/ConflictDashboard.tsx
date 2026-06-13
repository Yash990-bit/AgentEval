import React, { useEffect, useState, useMemo } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Table, TableHeader, TableBody, TableHead, TableRow, TableCell } from '@/components/ui/table';

// Define the shape of a conflict payload from AABS
interface ConflictEvent {
  id: string;
  simulation_id: string;
  type: string; // e.g. 'Goal Conflict', 'Resource Conflict', etc.
  tick: number;
  agents: string[];
  severity: number; // 0.0 - 1.0
  root_cause: string;
  suggested_resolution: string;
  status: string; // e.g. 'active', 'auto_resolved', etc.
  timestamp?: string;
}

export interface AgentNode {
  id: string;
  x?: number;
  y?: number;
}

export interface LinkEdge {
  source: string;
  target: string;
}

export default function ConflictDashboard({ agents, links }: { agents: AgentNode[]; links: LinkEdge[] }) {
  const [activeConflicts, setActiveConflicts] = useState<ConflictEvent[]>([]);
  const [conflictHistory, setConflictHistory] = useState<ConflictEvent[]>([]);
  const [selectedFilter, setSelectedFilter] = useState<string>('All');
  const [activeTab, setActiveTab] = useState<'active' | 'timeline'>('active');

  useEffect(() => {
    // Establish real-time WebSocket connection to conflict endpoint
    const getWsUrl = () => {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      if (apiUrl) {
        try {
          const urlObj = new URL(apiUrl);
          const wsProtocol = urlObj.protocol === 'https:' ? 'wss:' : 'ws:';
          let path = urlObj.pathname.replace(/\/+$/, '');
          if (!path.endsWith('/api') && !path.includes('/api/v1')) {
            path = `${path}/api`;
          }
          return `${wsProtocol}//${urlObj.host}${path}/v1/conflicts/ws`;
        } catch (e) {
          console.error('Failed to parse NEXT_PUBLIC_API_URL, using fallback', e);
        }
      }
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      // Fallback for local development vs same-origin proxy
      if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return `ws://${window.location.hostname}:8000/api/v1/conflicts/ws`;
      }
      return `${wsProtocol}//${window.location.host}/api/v1/conflicts/ws`;
    };

    const wsUrl = getWsUrl();
    const ws = new WebSocket(wsUrl);
    
    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        // Ignore initialization greeting payload
        if (payload.id === 'init') return;

        const timestampedEvent: ConflictEvent = {
          ...payload,
          timestamp: new Date().toISOString(),
        };

        // Add to chronological event log timeline
        setConflictHistory((prev) => [timestampedEvent, ...prev]);

        // Maintain list of current active conflicts
        setActiveConflicts((prev) => {
          // If conflict is auto_resolved/manually_resolved, update or remove
          const index = prev.findIndex((c) => c.id === timestampedEvent.id);
          if (timestampedEvent.status !== 'active') {
            if (index !== -1) {
              // Update state to reflect resolution
              const copy = [...prev];
              copy[index] = timestampedEvent;
              return copy;
            }
            return prev;
          } else {
            if (index !== -1) {
              const copy = [...prev];
              copy[index] = timestampedEvent;
              return copy;
            }
            return [timestampedEvent, ...prev];
          }
        });
      } catch (e) {
        console.error('Failed to parse incoming conflict payload', e);
      }
    };

    ws.onerror = (err) => console.error('WebSocket connection error:', err);
    return () => ws.close();
  }, []);

  // Filter types list
  const conflictTypes = [
    'All',
    'Goal Conflict',
    'Resource Conflict',
    'Communication Conflict',
    'Trust Breakdown',
    'Deadlock',
    'Priority Inversion',
  ];

  // Filter and sort active conflicts by severity descending
  const filteredActiveConflicts = useMemo(() => {
    let list = [...activeConflicts];
    if (selectedFilter !== 'All') {
      list = list.filter((c) => c.type === selectedFilter);
    }
    // Sort by severity score descending (primary rule)
    return list.sort((a, b) => b.severity - a.severity);
  }, [activeConflicts, selectedFilter]);

  // Filter timeline history
  const filteredTimeline = useMemo(() => {
    let list = [...conflictHistory];
    if (selectedFilter !== 'All') {
      list = list.filter((c) => c.type === selectedFilter);
    }
    return list;
  }, [conflictHistory, selectedFilter]);

  // Severity Badge color selector helper
  const getSeverityBadge = (severity: number) => {
    if (severity >= 0.7) {
      return (
        <Badge variant="default" className="bg-red-500/20 text-red-400 border-red-500/30">
          High ({severity.toFixed(2)})
        </Badge>
      );
    } else if (severity >= 0.4) {
      return (
        <Badge variant="default" className="bg-amber-500/20 text-amber-400 border-amber-500/30">
          Medium ({severity.toFixed(2)})
        </Badge>
      );
    } else {
      return (
        <Badge variant="default" className="bg-blue-500/20 text-blue-400 border-blue-500/30">
          Low ({severity.toFixed(2)})
        </Badge>
      );
    }
  };

  // Status Badge color selector helper
  const getStatusBadge = (status: string) => {
    const s = status.toLowerCase();
    if (s === 'active') {
      return (
        <Badge variant="outline" className="border-red-500/50 text-red-400 bg-red-950/20 animate-pulse">
          Active
        </Badge>
      );
    } else if (s === 'auto_resolved') {
      return (
        <Badge variant="outline" className="border-emerald-500/50 text-emerald-400 bg-emerald-950/20">
          Auto Resolved
        </Badge>
      );
    } else if (s === 'manually_resolved') {
      return (
        <Badge variant="outline" className="border-blue-500/50 text-blue-400 bg-blue-950/20">
          Resolved
        </Badge>
      );
    } else {
      return <Badge variant="outline" className="border-slate-500 text-slate-400">{status}</Badge>;
    }
  };

  return (
    <Card className="border border-white/10 bg-black/40 backdrop-blur-xl shadow-2xl overflow-hidden rounded-xl">
      <CardHeader className="border-b border-white/10 bg-white/5 px-6 py-4 flex flex-row items-center justify-between">
        <div>
          <CardTitle className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-red-500 animate-ping"></span>
            Conflict Detection Dashboard
          </CardTitle>
          <p className="text-xs text-slate-400 mt-1">Real-time background agent conflict monitoring</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('active')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'active'
                ? 'bg-primary text-primary-foreground shadow-md'
                : 'bg-white/5 hover:bg-white/10 text-slate-300'
            }`}
          >
            Active ({filteredActiveConflicts.length})
          </button>
          <button
            onClick={() => setActiveTab('timeline')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'timeline'
                ? 'bg-primary text-primary-foreground shadow-md'
                : 'bg-white/5 hover:bg-white/10 text-slate-300'
            }`}
          >
            Timeline Log ({filteredTimeline.length})
          </button>
        </div>
      </CardHeader>

      {/* Filter panel */}
      <div className="px-6 py-3 border-b border-white/10 bg-white/2 flex items-center justify-between gap-4 overflow-x-auto">
        <span className="text-xs font-semibold text-slate-400 whitespace-nowrap">Filter Type:</span>
        <div className="flex gap-1.5 overflow-x-auto pb-1 scrollbar-thin">
          {conflictTypes.map((t) => (
            <button
              key={t}
              onClick={() => setSelectedFilter(t)}
              className={`px-2.5 py-1 rounded-full text-xs transition-all whitespace-nowrap ${
                selectedFilter === t
                  ? 'bg-white/20 text-white font-medium border border-white/20'
                  : 'bg-white/5 hover:bg-white/10 text-slate-400 hover:text-slate-200 border border-transparent'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      <CardContent className="p-0 max-h-[550px] overflow-y-auto">
        {activeTab === 'active' ? (
          filteredActiveConflicts.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-12 text-center">
              <div className="h-12 w-12 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-500 text-lg mb-3">✓</div>
              <p className="text-sm font-semibold text-slate-300">System Harmonized</p>
              <p className="text-xs text-slate-500 mt-1">No active conflicts detected in this simulation</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead className="text-xs text-slate-400 font-semibold uppercase">Type</TableHead>
                  <TableHead className="text-xs text-slate-400 font-semibold uppercase">Severity</TableHead>
                  <TableHead className="text-xs text-slate-400 font-semibold uppercase">Agents Involved</TableHead>
                  <TableHead className="text-xs text-slate-400 font-semibold uppercase">Tick</TableHead>
                  <TableHead className="text-xs text-slate-400 font-semibold uppercase">Root Cause</TableHead>
                  <TableHead className="text-xs text-slate-400 font-semibold uppercase">Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredActiveConflicts.map((c) => (
                  <TableRow key={c.id} className="hover:bg-white/5 transition-colors">
                    <TableCell className="font-semibold text-slate-200">{c.type}</TableCell>
                    <TableCell>{getSeverityBadge(c.severity)}</TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {c.agents.map((a) => (
                          <span key={a} className="text-[10px] bg-white/5 px-2 py-0.5 rounded text-slate-300 font-mono">
                            {a.slice(0, 8)}...
                          </span>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell className="text-slate-400 font-mono text-xs">{c.tick}</TableCell>
                    <TableCell className="max-w-[200px] truncate text-slate-300 text-xs" title={c.root_cause}>
                      {c.root_cause}
                    </TableCell>
                    <TableCell>{getStatusBadge(c.status)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )
        ) : filteredTimeline.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-12 text-center text-slate-500 text-sm">
            No events logged in the timeline yet.
          </div>
        ) : (
          <div className="p-6 space-y-4">
            {filteredTimeline.map((e, idx) => (
              <div key={e.id + '_' + idx} className="relative pl-6 border-l border-white/10 last:border-0 pb-4">
                <div className="absolute -left-[5px] top-1.5 h-2.5 w-2.5 rounded-full bg-primary border-2 border-black" />
                <div className="flex items-center justify-between gap-4">
                  <span className="text-xs font-semibold text-slate-200">{e.type} Detected</span>
                  <span className="text-[10px] text-slate-500">
                    {e.timestamp ? new Date(e.timestamp).toLocaleTimeString() : 'Tick ' + e.tick}
                  </span>
                </div>
                <p className="text-xs text-slate-300 mt-1">{e.root_cause}</p>
                <div className="flex items-center gap-2 mt-2">
                  <Badge variant="outline" className="text-[9px] px-1.5 py-0 border-white/10 text-slate-400">
                    Tick {e.tick}
                  </Badge>
                  <span className="text-[10px] text-emerald-400 font-medium">
                    Suggested Resolution: {e.suggested_resolution}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

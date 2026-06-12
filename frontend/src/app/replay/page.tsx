"use client";
import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, X, Terminal, Cpu, Clock, RefreshCw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { GlassCard } from '@/components/ui/GlassCard';
import { GoldButton } from '@/components/ui/GoldButton';

interface Replay {
  name: string;
  date: string;
  duration: string;
  maxTicks: number;
  logs: string[];
}

const replays: Replay[] = [
  {
    name: 'Project Nexus Alpha',
    date: '2026-06-01',
    duration: '3m 12s',
    maxTicks: 200,
    logs: [
      "Initializing Nexus Alpha simulation environment...",
      "Spawning agent ARIA-7 (Coordinator) at canvas position (0, 0)",
      "Spawning agent NEXUS-3 (Researcher) at canvas position (200, 0)",
      "Spawning agent ECHO-1 (Analyst) at canvas position (100, 150)",
      "Establishing trust bonds: ARIA-7 <-> NEXUS-3 (0.90), NEXUS-3 <-> ECHO-1 (0.85)",
      "Simulating task delegation: ARIA-7 requests research on Token Optimization.",
      "NEXUS-3 starts computational search on vector database...",
      "ECHO-1 starts monitoring resource usage rates...",
      "Resource warning: Compute capacity reaching 78% threshold.",
      "Conflict detected: NEXUS-3 and ECHO-1 request overlapping GPU threads.",
      "Analyzing conflict severity: High (0.84). Type: Resource Exhaustion.",
      "Conflict mitigation proposal injected: Assign thread priority to NEXUS-3.",
      "Mitigation applied. Thread allocation resolved successfully.",
      "Consensus restored across agent collective.",
      "Simulation completed. Final success rate: 94.2%."
    ]
  },
  {
    name: 'Operation Hivemind',
    date: '2026-05-20',
    duration: '2m 45s',
    maxTicks: 150,
    logs: [
      "Initializing Operation Hivemind environment...",
      "Spawning agents in swarm configuration...",
      "Swarm communication channels verified. Encryption: Active.",
      "Goal set: Global dataset consensus.",
      "Tick 12: Consensus rate at 34%.",
      "Tick 40: Warning - latency mismatch on node ECHO-1.",
      "Tick 68: Divergence alert. ECHO-1 goal priorities disagree with core coordinator.",
      "Consensus paused. Negotiating priorities...",
      "Negotiation successful. Trust factor lowered temporarily.",
      "Consensus resumed. Success rate at 88.5%.",
      "Hivemind objectives reached.",
      "Simulation finished."
    ]
  },
];

export default function ReplayCenterPage() {
  const [activeReplay, setActiveReplay] = useState<Replay | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTick, setCurrentTick] = useState(0);
  const [speed, setSpeed] = useState<1 | 2 | 4>(1);
  const [visibleLogs, setVisibleLogs] = useState<string[]>([]);
  const consoleEndRef = useRef<HTMLDivElement>(null);

  // Playback timer
  useEffect(() => {
    if (!activeReplay || !isPlaying) return;

    const intervalTime = 100 / speed; // baseline rate
    const timer = setInterval(() => {
      setCurrentTick(tick => {
        if (tick >= activeReplay.maxTicks) {
          setIsPlaying(false);
          return activeReplay.maxTicks;
        }
        return tick + 1;
      });
    }, intervalTime);

    return () => clearInterval(timer);
  }, [activeReplay, isPlaying, speed]);

  // Sync logs to current tick progress
  useEffect(() => {
    if (!activeReplay) return;
    const totalLogsCount = activeReplay.logs.length;
    const ratio = currentTick / activeReplay.maxTicks;
    const logsToShowCount = Math.min(totalLogsCount, Math.ceil(ratio * totalLogsCount));
    setVisibleLogs(activeReplay.logs.slice(0, logsToShowCount));
  }, [currentTick, activeReplay]);

  // Scroll to bottom of terminal feed
  useEffect(() => {
    consoleEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [visibleLogs]);

  const handleStartReplay = (replay: Replay) => {
    setActiveReplay(replay);
    setCurrentTick(0);
    setIsPlaying(true);
    setVisibleLogs([]);
  };

  const handleReset = () => {
    setCurrentTick(0);
    setIsPlaying(false);
    setVisibleLogs([]);
  };

  return (
    <div className="p-8 relative">
      <AnimatePresence>
        {!activeReplay ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <GlassCard className="p-8">
              <h3 className="text-2xl font-bold mb-6 text-gold-primary">Replay Center</h3>
              <p className="text-sm text-gray-400 mb-6">Analyze and play back historic logs from previous autonomous agent simulations.</p>
              
              <ul className="space-y-4">
                {replays.map((r, idx) => (
                  <li key={idx} className="flex items-center justify-between p-4 border border-gold-primary/10 rounded-lg bg-black/40 hover:border-gold-primary/30 transition-all">
                    <div>
                      <p className="text-white font-semibold text-lg">{r.name}</p>
                      <p className="text-sm text-gray-400 mt-1">{r.date} • {r.duration} • {r.maxTicks} total ticks</p>
                    </div>
                    <GoldButton variant="primary" className="px-5 py-2 text-sm" onClick={() => handleStartReplay(r)}>
                      Replay
                    </GoldButton>
                  </li>
                ))}
              </ul>
            </GlassCard>
          </motion.div>
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
          >
            <GlassCard className="p-6 flex flex-col min-h-[550px] relative">
              {/* Header */}
              <div className="flex justify-between items-center mb-6 pb-4 border-b border-gold-primary/10">
                <div>
                  <h4 className="text-xl font-bold text-white flex items-center gap-2">
                    <RefreshCw className="text-gold-primary animate-spin-slow" size={20} />
                    {activeReplay.name}
                  </h4>
                  <p className="text-xs text-gray-400 mt-1">Simulated historic session playback</p>
                </div>
                <button
                  onClick={() => setActiveReplay(null)}
                  className="p-1.5 hover:bg-gold-primary/10 rounded text-gray-400 hover:text-white transition-colors"
                >
                  <X size={20} />
                </button>
              </div>

              {/* Controls Panel */}
              <div className="flex flex-wrap items-center justify-between gap-4 p-4 border border-gold-primary/20 rounded-lg bg-black/50 mb-6">
                <div className="flex items-center gap-3">
                  <GoldButton variant="outline" className="p-2" onClick={() => setIsPlaying(!isPlaying)}>
                    {isPlaying ? <Pause size={16} /> : <Play size={16} />}
                  </GoldButton>
                  <GoldButton variant="outline" className="p-2" onClick={handleReset}>
                    <RotateCcw size={16} />
                  </GoldButton>

                  <div className="h-6 w-px bg-gold-primary/20 mx-1"></div>

                  <span className="text-xs text-gray-400">Speed:</span>
                  <div className="flex bg-black/60 rounded border border-gold-primary/20 p-0.5">
                    {([1, 2, 4] as const).map(s => (
                      <button
                        key={s}
                        onClick={() => setSpeed(s)}
                        className={`px-2 py-0.5 text-xs font-semibold rounded transition-all ${
                          speed === s ? 'bg-gold-primary text-black font-bold' : 'text-gray-400 hover:text-white'
                        }`}
                      >
                        {s}x
                      </button>
                    ))}
                  </div>
                </div>

                <div className="flex items-center gap-4 text-xs font-mono text-gray-300">
                  <span className="flex items-center gap-1.5"><Clock size={14} className="text-gold-soft" /> Tick: {currentTick} / {activeReplay.maxTicks}</span>
                  <span className="flex items-center gap-1.5"><Cpu size={14} className="text-gold-soft" /> Status: {currentTick >= activeReplay.maxTicks ? 'Finished' : isPlaying ? 'Playing' : 'Paused'}</span>
                </div>
              </div>

              {/* Scrubber */}
              <div className="mb-6 px-1">
                <input
                  type="range"
                  min={0}
                  max={activeReplay.maxTicks}
                  value={currentTick}
                  onChange={(e) => {
                    setCurrentTick(parseInt(e.target.value));
                    setIsPlaying(false);
                  }}
                  className="w-full cursor-pointer accent-gold-primary"
                />
                <div className="flex justify-between text-[10px] text-gray-400 mt-1">
                  <span>Tick 0</span>
                  <span>Tick {Math.round(activeReplay.maxTicks / 2)}</span>
                  <span>Tick {activeReplay.maxTicks}</span>
                </div>
              </div>

              {/* Terminal / Logger */}
              <div className="flex-1 min-h-[200px] bg-black/90 border border-gold-primary/20 rounded-lg p-4 font-mono text-sm overflow-y-auto flex flex-col gap-2 shadow-inner">
                <div className="flex items-center gap-2 text-gold-primary border-b border-gold-primary/10 pb-2 mb-2">
                  <Terminal size={16} />
                  <span className="text-xs font-semibold uppercase tracking-wider">Agent Event Log Console</span>
                </div>
                
                <div className="flex-1 overflow-y-auto space-y-2 max-h-[250px] pr-1">
                  {visibleLogs.length === 0 && (
                    <p className="text-gray-500 italic text-xs">Awaiting log signal...</p>
                  )}
                  {visibleLogs.map((log, i) => (
                    <div key={i} className="text-gray-300 leading-relaxed text-xs">
                      <span className="text-gold-primary font-bold mr-2">&gt;</span>
                      {log}
                    </div>
                  ))}
                  <div ref={consoleEndRef} />
                </div>
              </div>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

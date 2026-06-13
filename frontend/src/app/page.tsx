"use client";
import React, { useState, useEffect, useRef, useMemo } from 'react';
import { create } from 'zustand';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  FlaskConical,
  Bot,
  Network,
  BarChart3,
  PlayCircle,
  Settings,
  Activity,
  AlertTriangle,
  TrendingUp,
  Zap,
  Shield,
  Search,
  Bell,
  User,
  Plus,
  X,
  Play,
  Pause,
  SkipBack,
  SkipForward,
  RotateCcw,
  Copy,
  Check,
  CheckCircle,
  Sliders,
  Layers,
  AlertOctagon,
  Info,
  Lock,
  Eye,
  EyeOff,
  Briefcase,
  Cpu,
  History,
  Sparkles,
  Clock,
  ArrowRight,
  DollarSign,
  Globe,
  SlidersHorizontal,
  PlusCircle,
  Trash2
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip as ReTooltip,
  ResponsiveContainer,
  RadialBarChart,
  RadialBar,
  BarChart,
  Bar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  LineChart,
  Line,
  Legend,
  Cell,
  PieChart,
  Pie
} from 'recharts';

/* =========================================================================
   1. DESIGN SYSTEM & CSS VARIABLES
   ========================================================================= */
const designStyle = `
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;0,700;1,300&family=DM+Sans:ital,opsz,wght@0,9..40,100..1000;1,9..40,100..1000&family=JetBrains+Mono:ital,wght@0,100..800;1,100..800&display=swap');

  :root {
    --bg-base: #0C0A09;
    --bg-surface: #161311;
    --bg-card: #1D1917;
    --bg-card-hover: #26211E;
    --gold-primary: #D4AF37;
    --gold-secondary: #FFD700;
    --gold-soft: #F5D76E;
    --gold-dim: #8B6914;
    --text-primary: #FFFFFF;
    --text-secondary: #B3B3B3;
    --text-muted: #666666;
    --danger: #FF4444;
    --success: #00C896;
    --warning: #FF9500;
    --info: #4A9EFF;
    --black: #000000;
  }

  .font-display { font-family: 'Cormorant Garamond', serif; }
  .font-ui { font-family: 'DM Sans', sans-serif; }
  .font-mono { font-family: 'JetBrains Mono', monospace; }

  /* Premium scrollbar override */
  ::-webkit-scrollbar {
    width: 4px;
    height: 4px;
  }
  ::-webkit-scrollbar-track {
    background: transparent;
  }
  ::-webkit-scrollbar-thumb {
    background: var(--gold-primary);
    border-radius: 2px;
  }

  /* Scanline effect for events feed */
  .scanlines {
    position: relative;
    overflow: hidden;
  }
  .scanlines::before {
    content: " ";
    display: block;
    position: absolute;
    top: 0; left: 0; bottom: 0; right: 0;
    background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
    z-index: 10;
    background-size: 100% 3px, 3px 100%;
    pointer-events: none;
  }

  /* Shimmer button animation */
  .btn-shimmer {
    position: relative;
    overflow: hidden;
  }
  .btn-shimmer::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -60%;
    width: 30%;
    height: 200%;
    background: rgba(255, 255, 255, 0.15);
    transform: rotate(30deg);
    transition: none;
  }
  .btn-shimmer:hover::after {
    left: 150%;
    transition: all 0.6s ease-in-out;
  }
`;

/* =========================================================================
   2. TYPES & INTERFACES
   ========================================================================= */
interface Agent {
  id: string;
  name: string;
  role: string;
  description: string;
  status: 'running' | 'idle' | 'failed' | 'sleeping';
  trust: number;
  energy: number;
  risk: number;
  goalsCompleted: number;
  messagesSent: number;
  conflictsInvolved: number;
  tokensUsed: string;
}

interface Simulation {
  id: string;
  name: string;
  agents: number;
  ticks: number;
  status: 'running' | 'paused' | 'completed' | 'failed';
  success: number;
  conflicts: number;
  started: string;
}

interface Conflict {
  id: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  agents: string[];
  type: string;
  time: string;
  tick: number;
}

interface Goal {
  id: string;
  agentId: string;
  title: string;
  progress: number;
  status: 'completed' | 'active' | 'failed' | 'abandoned';
  priority: 'high' | 'medium' | 'low';
  deadline: number;
}

interface FeedEvent {
  tick: number;
  type: 'think' | 'tool' | 'message' | 'conflict' | 'goal';
  text: string;
  agent: string;
}

/* =========================================================================
   3. ZUSTAND OBSERVABILITY STORE
   ========================================================================= */
interface Store {
  currentPage: string;
  sidebarOpen: boolean;
  selectedSimulationId: string;
  selectedAgentId: string;
  activeSimulations: Simulation[];
  agents: Agent[];
  conflicts: Conflict[];
  feedEvents: FeedEvent[];
  goals: Goal[];
  playbackTick: number;
  playbackRunning: boolean;
  playbackSpeed: number;
  apiKeys: any[];
  auditLogs: any[];
  workspaces: any[];
  members: any[];
  setCurrentPage: (page: string) => void;
  setSidebarOpen: (open: boolean) => void;
  setSelectedSimulationId: (id: string) => void;
  setSelectedAgentId: (id: string) => void;
  resolveConflict: (id: string) => void;
  stopSimulation: (id: string) => void;
  setPlaybackTick: (tick: number) => void;
  setPlaybackRunning: (running: boolean) => void;
  setPlaybackSpeed: (speed: number) => void;
  addSimulation: (sim: Simulation) => void;
  addApiKey: (key: any) => void;
  revokeApiKey: (id: string) => void;
  addMember: (member: any) => void;
}

const useStore = create<Store>((set) => ({
  currentPage: 'dashboard',
  sidebarOpen: true,
  selectedSimulationId: 'sim-1',
  selectedAgentId: 'agent-1',
  activeSimulations: [
    { id: 'sim-1', name: 'Project Nexus Alpha', agents: 12, ticks: 340, status: 'running', success: 94.2, conflicts: 3, started: '2026-06-01' },
    { id: 'sim-2', name: 'Operation Hivemind', agents: 8, ticks: 150, status: 'paused', success: 88.5, conflicts: 1, started: '2026-05-20' },
    { id: 'sim-3', name: 'Research Sprint Q4', agents: 6, ticks: 400, status: 'completed', success: 91.0, conflicts: 0, started: '2026-05-18' },
    { id: 'sim-4', name: 'Security Audit Sim', agents: 10, ticks: 210, status: 'failed', success: 42.4, conflicts: 5, started: '2026-05-15' },
    { id: 'sim-5', name: 'Trading Desk Mirror', agents: 15, ticks: 500, status: 'running', success: 96.1, conflicts: 2, started: '2026-06-03' },
    { id: 'sim-6', name: 'Support Team Twin', agents: 4, ticks: 120, status: 'completed', success: 89.9, conflicts: 1, started: '2026-05-28' },
    { id: 'sim-7', name: 'Conflict Stress Test', agents: 20, ticks: 90, status: 'running', success: 72.8, conflicts: 8, started: '2026-06-05' },
    { id: 'sim-8', name: 'Digital Twin Corp', agents: 12, ticks: 300, status: 'completed', success: 95.0, conflicts: 0, started: '2026-05-25' }
  ],
  agents: [
    { id: 'agent-1', name: 'ARIA-7', role: 'Coordinator', description: 'Orchestrates workflow delegation and consensus rules.', status: 'running', trust: 0.85, energy: 0.92, risk: 0.12, goalsCompleted: 15, messagesSent: 432, conflictsInvolved: 1, tokensUsed: '1.2M' },
    { id: 'agent-2', name: 'NEXUS-3', role: 'Researcher', description: 'Performs semantic searches and knowledge aggregation.', status: 'running', trust: 0.92, energy: 0.78, risk: 0.08, goalsCompleted: 12, messagesSent: 290, conflictsInvolved: 0, tokensUsed: '890k' },
    { id: 'agent-3', name: 'ECHO-1', role: 'Analyst', description: 'Evaluates agent performance metrics and safety metrics.', status: 'running', trust: 0.74, energy: 0.84, risk: 0.22, goalsCompleted: 9, messagesSent: 198, conflictsInvolved: 2, tokensUsed: '640k' },
    { id: 'agent-4', name: 'PLATO-5', role: 'Researcher', description: 'Hypothesis generation and reasoning verification.', status: 'idle', trust: 0.88, energy: 0.65, risk: 0.15, goalsCompleted: 10, messagesSent: 310, conflictsInvolved: 1, tokensUsed: '920k' },
    { id: 'agent-5', name: 'KANT-2', role: 'Planner', description: 'Decomposes macro instructions into sequential tasks.', status: 'running', trust: 0.95, energy: 0.89, risk: 0.05, goalsCompleted: 18, messagesSent: 512, conflictsInvolved: 0, tokensUsed: '1.5M' },
    { id: 'agent-6', name: 'SARA-8', role: 'Support', description: 'Interacts with simulated external user interfaces.', status: 'sleeping', trust: 0.80, energy: 0.50, risk: 0.18, goalsCompleted: 6, messagesSent: 120, conflictsInvolved: 1, tokensUsed: '400k' },
    { id: 'agent-7', name: 'VERA-9', role: 'Support', description: 'Fallback agent for tool failure remediation.', status: 'idle', trust: 0.76, energy: 0.72, risk: 0.14, goalsCompleted: 8, messagesSent: 165, conflictsInvolved: 0, tokensUsed: '530k' },
    { id: 'agent-8', name: 'ORION-4', role: 'Executor', description: 'Performs automated shell and code sandbox execution.', status: 'running', trust: 0.82, energy: 0.90, risk: 0.28, goalsCompleted: 14, messagesSent: 380, conflictsInvolved: 3, tokensUsed: '1.1M' },
    { id: 'agent-9', name: 'NOVA-2', role: 'Executor', description: 'File writer and asset compiler process.', status: 'failed', trust: 0.52, energy: 0.10, risk: 0.65, goalsCompleted: 4, messagesSent: 90, conflictsInvolved: 4, tokensUsed: '250k' },
    { id: 'agent-10', name: 'AURA-1', role: 'Negotiator', description: 'Resolves token allocation disputes between processes.', status: 'running', trust: 0.89, energy: 0.81, risk: 0.11, goalsCompleted: 11, messagesSent: 270, conflictsInvolved: 2, tokensUsed: '780k' },
    { id: 'agent-11', name: 'CYRUS-3', role: 'Security Auditor', description: 'Intercepts prompt injection vectors and tool abuse.', status: 'running', trust: 0.94, energy: 0.88, risk: 0.04, goalsCompleted: 16, messagesSent: 410, conflictsInvolved: 0, tokensUsed: '1.3M' },
    { id: 'agent-12', name: 'TACT-9', role: 'Planner', description: 'Alternative task scheduling under scarcity constraints.', status: 'sleeping', trust: 0.83, energy: 0.55, risk: 0.16, goalsCompleted: 7, messagesSent: 145, conflictsInvolved: 1, tokensUsed: '430k' }
  ],
  conflicts: [
    { id: 'conf-1', severity: 'critical', agents: ['ARIA-7', 'ECHO-1'], type: 'Resource Lock Deadlock', time: '2m ago', tick: 142 },
    { id: 'conf-2', severity: 'high', agents: ['NEXUS-3', 'ORION-4'], type: 'Goal Priority Divergence', time: '5m ago', tick: 128 },
    { id: 'conf-3', severity: 'medium', agents: ['ECHO-1', 'NOVA-2'], type: 'Memory Drift Divergence', time: '12m ago', tick: 95 }
  ],
  feedEvents: [
    { tick: 145, type: 'think', text: 'KANT-2 generating alternative tree-of-thought strategy for resource scarcity.', agent: 'KANT-2' },
    { tick: 145, type: 'tool', text: 'ORION-4 executed BashCommand: `npm run build` inside sandbox container.', agent: 'ORION-4' },
    { tick: 144, type: 'message', text: 'ARIA-7 dispatched consensus request to NEXUS-3 and ECHO-1.', agent: 'ARIA-7' },
    { tick: 143, type: 'conflict', text: 'Deadlock warning: ECHO-1 and ARIA-7 concurrently requested database write lock.', agent: 'ECHO-1' },
    { tick: 142, type: 'goal', text: 'CYRUS-3 completed safety evaluation audit for Agent Network.', agent: 'CYRUS-3' }
  ],
  goals: [
    { id: 'g-1', agentId: 'agent-1', title: 'Complete consensus validation pipeline', progress: 85, status: 'active', priority: 'high', deadline: 200 },
    { id: 'g-2', agentId: 'agent-1', title: 'Sync state metrics with Observability Hub', progress: 100, status: 'completed', priority: 'medium', deadline: 150 },
    { id: 'g-3', agentId: 'agent-2', title: 'Aggregate knowledge bases for Trading Desk', progress: 40, status: 'active', priority: 'high', deadline: 300 },
    { id: 'g-4', agentId: 'agent-3', title: 'Detect semantic drift parameters', progress: 95, status: 'active', priority: 'low', deadline: 250 },
    { id: 'g-5', agentId: 'agent-5', title: 'Resolve task priorities scheduler', progress: 100, status: 'completed', priority: 'high', deadline: 180 },
    { id: 'g-6', agentId: 'agent-9', title: 'Compile design tokens into index.css', progress: 20, status: 'failed', priority: 'high', deadline: 120 }
  ],
  playbackTick: 47,
  playbackRunning: false,
  playbackSpeed: 1,
  apiKeys: [
    { id: 'key-1', name: 'Gemini Production Key', scopes: 'read/write', created: '2026-05-10', lastUsed: '3m ago', requests: '1.2M', status: 'active', value: 'sk_live_gemini7482hsa0' },
    { id: 'key-2', name: 'OpenAI Observability ReadOnly', scopes: 'read-only', created: '2026-05-12', lastUsed: '1h ago', requests: '430k', status: 'active', value: 'sk_live_openaiajs8291n' },
    { id: 'key-3', name: 'Legacy Test Token', scopes: 'admin', created: '2026-04-01', lastUsed: '12d ago', requests: '12k', status: 'revoked', value: 'sk_test_legacytoken839' }
  ],
  auditLogs: [
    { id: 'log-1', timestamp: '2026-06-11 15:30:12', user: 'yash@google.com', action: 'CREATE', resource: 'Simulation Studio Scenario', ip: '10.229.12.98', details: 'Added simulated conflict rules threshold' },
    { id: 'log-2', timestamp: '2026-06-11 15:28:44', user: 'yash@google.com', action: 'UPDATE', resource: 'Agent ARIA-7 Config', ip: '10.229.12.98', details: 'Adjusted default memory decay parameter from 0.05 to 0.08' },
    { id: 'log-3', timestamp: '2026-06-11 15:15:20', user: 'yash@google.com', action: 'DELETE', resource: 'Mock Simulation Run #12', ip: '10.229.12.98', details: 'Removed stale session files' }
  ],
  workspaces: [
    { id: 'w-1', name: 'Core Observability Swarm', members: 4, simulations: 8 },
    { id: 'w-2', name: 'Fintech Simulation Desk', members: 6, simulations: 3 },
    { id: 'w-3', name: 'General Sandboxes', members: 2, simulations: 12 }
  ],
  members: [
    { id: 'm-1', name: 'Yash Raghubanshi (You)', role: 'Owner', lastActive: 'Active Now' }
  ],
  setCurrentPage: (page) => set({ currentPage: page }),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  setSelectedSimulationId: (id) => set({ selectedSimulationId: id }),
  setSelectedAgentId: (id) => set({ selectedAgentId: id }),
  resolveConflict: (id) => set((state) => ({
    conflicts: state.conflicts.filter(c => c.id !== id)
  })),
  stopSimulation: (id) => set((state) => ({
    activeSimulations: state.activeSimulations.map(sim =>
      sim.id === id ? { ...sim, status: 'completed', conflicts: 0 } : sim
    )
  })),
  setPlaybackTick: (tick) => set({ playbackTick: tick }),
  setPlaybackRunning: (running) => set({ playbackRunning: running }),
  setPlaybackSpeed: (speed) => set({ playbackSpeed: speed }),
  addSimulation: (sim) => set((state) => ({ activeSimulations: [sim, ...state.activeSimulations] })),
  addApiKey: (key) => set((state) => ({ apiKeys: [key, ...state.apiKeys] })),
  revokeApiKey: (id) => set((state) => ({
    apiKeys: state.apiKeys.map(k => k.id === id ? { ...k, status: 'revoked' } : k)
  })),
  addMember: (member) => set((state) => ({ members: [...state.members, member] }))
}));

/* =========================================================================
   4. CORE SHARED COMPONENT DEFINITIONS
   ========================================================================= */
const GoldButton: React.FC<{
  children: React.ReactNode;
  variant?: 'primary' | 'outline' | 'ghost';
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
}> = ({ children, variant = 'primary', className = '', onClick, disabled }) => {
  const baseStyle = "btn-shimmer font-ui px-4 py-2 rounded font-semibold transition-all duration-300 active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed";
  
  let variantStyle = "";
  let customStyle: React.CSSProperties | undefined = undefined;

  if (variant === 'primary') {
    variantStyle = "shadow-[0_2px_4px_rgba(0,0,0,0.2)] hover:shadow-[0_4px_8px_rgba(0,0,0,0.3)]";
    customStyle = {
      background: 'linear-gradient(135deg, var(--gold-dim) 0%, var(--gold-primary) 50%, #FFFFFF 100%)',
      color: '#000000',
    };
  } else if (variant === 'outline') {
    variantStyle = "border border-gold-primary text-gold-primary bg-transparent hover:bg-gold-primary/10";
  } else {
    variantStyle = "text-gray-400 hover:text-gold-primary hover:bg-white/5";
  }

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyle} ${variantStyle} ${className}`}
      style={customStyle}
    >
      {children}
    </button>
  );
};

const GlassCard: React.FC<{
  children: React.ReactNode;
  className?: string;
  glow?: boolean;
  gradientBorder?: boolean;
  onClick?: () => void;
}> = ({ children, className = '', glow = false, gradientBorder = false, onClick }) => {
  return (
    <div
      onClick={onClick}
      className={`glass-card rounded-xl p-6 transition-all duration-300 relative ${
        glow ? 'shadow-[0_0_30px_rgba(212,175,55,0.25)]' : ''
      } ${
        onClick ? 'cursor-pointer hover:scale-[1.01]' : ''
      } ${className}`}
      style={{
        background: 'rgba(26, 26, 26, 0.8)',
        backdropFilter: 'blur(20px)',
        border: '1px solid rgba(212, 175, 55, 0.15)',
        ...(gradientBorder ? {
          borderImage: 'linear-gradient(135deg, #D4AF37, transparent, #D4AF37) 1'
        } : {})
      }}
    >
      {children}
    </div>
  );
};

const StatusBadge: React.FC<{
  status: string;
  className?: string;
}> = ({ status, className = '' }) => {
  const norm = status.toLowerCase();
  let color = "bg-gray-500/20 text-gray-400 border border-gray-500/30";
  
  if (norm === 'running' || norm === 'active' || norm === 'success' || norm === 'low') {
    color = "bg-[#00C896]/20 text-[#00C896] border border-[#00C896]/30 animate-pulse";
  } else if (norm === 'paused' || norm === 'medium' || norm === 'warning') {
    color = "bg-[#FF9500]/20 text-[#FF9500] border border-[#FF9500]/30";
  } else if (norm === 'failed' || norm === 'critical' || norm === 'high') {
    color = "bg-[#FF4444]/20 text-[#FF4444] border border-[#FF4444]/30";
  } else if (norm === 'sleeping' || norm === 'completed') {
    color = "bg-[#4A9EFF]/20 text-[#4A9EFF] border border-[#4A9EFF]/30";
  }

  return (
    <span className={`px-2 py-0.5 text-[10px] font-mono font-bold uppercase rounded ${color} ${className}`}>
      {status}
    </span>
  );
};

const AgentAvatar: React.FC<{
  role: string;
  size?: number;
  className?: string;
}> = ({ role, size = 40, className = '' }) => {
  // Generates custom SVG geometric pattern based on role
  const getPattern = () => {
    switch (role.toLowerCase()) {
      case 'coordinator':
        return <polygon points="20,5 35,15 35,30 20,40 5,30 5,15" fill="none" stroke="var(--gold-primary)" strokeWidth="2" />;
      case 'planner':
        return <rect x="8" y="8" width="24" height="24" rx="4" fill="none" stroke="var(--gold-soft)" strokeWidth="2" />;
      case 'researcher':
        return <circle cx="20" cy="20" r="15" fill="none" stroke="var(--gold-secondary)" strokeWidth="2" />;
      case 'analyst':
        return <path d="M20,5 L35,35 L5,35 Z" fill="none" stroke="var(--info)" strokeWidth="2" />;
      case 'security auditor':
        return <path d="M20,5 L35,12 L35,28 L20,35 L5,28 L5,12 Z" fill="none" stroke="var(--success)" strokeWidth="2" />;
      default:
        return <polygon points="20,10 30,20 20,30 10,20" fill="none" stroke="var(--gold-dim)" strokeWidth="2" />;
    }
  };

  return (
    <svg width={size} height={size} viewBox="0 0 40 40" className={`${className} bg-black/60 rounded-lg border border-gold-primary/20 p-1`}>
      {getPattern()}
    </svg>
  );
};

const GoldProgressBar: React.FC<{
  value: number; // 0 to 1
  className?: string;
}> = ({ value, className = '' }) => {
  return (
    <div className={`w-full bg-black/40 h-2 rounded border border-gold-primary/10 overflow-hidden ${className}`}>
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${Math.min(100, value * 100)}%` }}
        transition={{ duration: 1, ease: 'easeOut' }}
        className="h-full bg-gradient-to-r from-gold-dim via-gold-primary to-gold-soft shadow-[0_0_10px_rgba(212,175,55,0.4)]"
      />
    </div>
  );
};

/* =========================================================================
   5. PAGE RENDERING UTILITIES
   ========================================================================= */

// --- KPI Count up hook ---
const useCountUp = (target: number, duration: number = 1500) => {
  const [val, setVal] = useState(0);

  useEffect(() => {
    let start = 0;
    const end = target;
    if (start === end) return;

    const totalMiliseconds = duration;
    const incrementTime = 40;
    const totalSteps = totalMiliseconds / incrementTime;
    const increment = (end - start) / totalSteps;

    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        clearInterval(timer);
        setVal(end);
      } else {
        setVal(Math.floor(start));
      }
    }, incrementTime);

    return () => clearInterval(timer);
  }, [target]);

  return val;
};

// --- KPI Card ---
const MetricCard: React.FC<{
  label: string;
  value: number;
  icon: any;
  accent: string;
  isRate?: boolean;
  isToken?: boolean;
}> = ({ label, value, icon: Icon, accent, isRate = false, isToken = false }) => {
  const count = useCountUp(isRate ? 94 : isToken ? 2.4 : value);
  const formattedVal = isRate ? `${count}.2%` : isToken ? `${count.toFixed(1)}M` : count;

  return (
    <GlassCard className="flex flex-col p-4 relative overflow-hidden group">
      <div className="absolute top-2 right-2 opacity-10 group-hover:opacity-20 transition-all duration-300">
        <Icon size={48} className={accent} />
      </div>
      <span className="text-xs text-text-secondary font-semibold uppercase font-ui tracking-wider">{label}</span>
      <div className="flex items-center justify-between mt-3">
        <span className="text-2xl font-bold text-white font-mono">{formattedVal}</span>
        <Icon size={20} className={accent} />
      </div>
      <div className="mt-2 flex items-center gap-1 text-[10px] text-success">
        <span>▲ 4.2%</span>
        <span className="text-text-muted font-ui">vs last hour</span>
      </div>
    </GlassCard>
  );
};

/* =========================================================================
   6. SUB-PAGES COMPONENTS
   ========================================================================= */

// ==================== PAGE 1: OBSERVABILITY DASHBOARD ====================
const DashboardPage: React.FC = () => {
  const store = useStore();
  const [notification, setNotification] = useState<string | null>(null);

  const handleResolve = (id: string, type: string) => {
    store.resolveConflict(id);
    setNotification(`Resolved conflict: ${type}`);
    setTimeout(() => setNotification(null), 3000);
  };

  const handleStop = (id: string, name: string) => {
    store.stopSimulation(id);
    setNotification(`Stopped simulation: ${name}`);
    setTimeout(() => setNotification(null), 3000);
  };

  return (
    <div className="space-y-6">
      {/* Toast alert */}
      <AnimatePresence>
        {notification && (
          <motion.div
            initial={{ opacity: 0, y: -20, x: 20 }}
            animate={{ opacity: 1, y: 0, x: 0 }}
            exit={{ opacity: 0, y: -20, x: 20 }}
            className="fixed top-20 right-8 z-50 flex items-center gap-3 px-4 py-3 bg-black/90 border border-gold-primary/30 rounded-lg shadow-[0_0_15px_rgba(212,175,55,0.25)] backdrop-blur-md"
          >
            <CheckCircle size={18} className="text-gold-primary animate-pulse" />
            <span className="text-sm font-semibold text-white">{notification}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <MetricCard label="Active Simulations" value={12} icon={Activity} accent="text-gold-primary" />
        <MetricCard label="Running Agents" value={847} icon={Bot} accent="text-[#00C896]" />
        <MetricCard label="Conflict Alerts" value={store.conflicts.length} icon={AlertTriangle} accent="text-[#FF4444]" />
        <MetricCard label="Success Rate" value={94} icon={TrendingUp} accent="text-gold-primary" isRate />
        <MetricCard label="Tokens Used Today" value={2} icon={Zap} accent="text-gold-soft" isToken />
        <MetricCard label="Avg Trust Score" value={78} icon={Shield} accent="text-info" />
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Live Simulation Chart */}
        <GlassCard className="lg:col-span-2 h-96 flex flex-col justify-between">
          <div className="flex justify-between items-center mb-4">
            <h4 className="font-display text-xl text-gold-primary font-semibold">Live Simulation Activity</h4>
            <StatusBadge status="running" />
          </div>
          <div className="flex-1 min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={[
                  { tick: 1, agents: 500, conflicts: 1 },
                  { tick: 5, agents: 520, conflicts: 2 },
                  { tick: 10, agents: 560, conflicts: 1 },
                  { tick: 15, agents: 640, conflicts: 3 },
                  { tick: 20, agents: 730, conflicts: 0 },
                  { tick: 24, agents: 847, conflicts: 2 }
                ]}
              >
                <defs>
                  <linearGradient id="colorGreen" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00C896" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#00C896" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorOrange" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#FF9500" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#FF9500" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="tick" stroke="rgba(212,175,55,0.3)" fontStyle="monospace" fontSize={10} />
                <YAxis stroke="rgba(212,175,55,0.3)" fontStyle="monospace" fontSize={10} />
                <ReTooltip 
                  contentStyle={{ backgroundColor: 'rgba(26,26,26,0.95)', border: '1px solid rgba(212,175,55,0.3)', color: '#fff' }} 
                  cursor={{ stroke: 'rgba(212,175,55,0.2)', strokeWidth: 1 }}
                />
                <Area type="monotone" dataKey="agents" stroke="#00C896" fillOpacity={1} fill="url(#colorGreen)" name="Active Agents" />
                <Area type="monotone" dataKey="conflicts" stroke="#FF9500" fillOpacity={1} fill="url(#colorOrange)" name="Conflicts" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        {/* Conflict Alerts */}
        <GlassCard className="h-96 flex flex-col">
          <h4 className="font-display text-xl text-gold-primary font-semibold mb-4 flex items-center gap-2">
            <AlertTriangle className="text-danger" size={20} />
            Conflict Alerts
          </h4>
          <div className="flex-1 overflow-y-auto space-y-3 pr-1">
            {store.conflicts.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center text-text-muted">
                <CheckCircle size={36} className="text-success mb-2" />
                <p className="text-sm">All Swarms Harmonized</p>
              </div>
            ) : (
              store.conflicts.map((c) => (
                <div key={c.id} className="p-3 bg-black/40 border border-gold-primary/10 rounded-lg flex flex-col gap-2 relative overflow-hidden group">
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-danger" />
                  <div className="flex justify-between items-center">
                    <StatusBadge status={c.severity} />
                    <span className="text-[10px] text-text-muted font-mono">{c.time}</span>
                  </div>
                  <p className="text-xs font-semibold text-white font-mono">{c.type}</p>
                  <p className="text-[10px] text-text-secondary">Agents: {c.agents.join(' ⇄ ')}</p>
                  <div className="flex justify-end">
                    <GoldButton variant="outline" className="px-2.5 py-1 text-[10px]" onClick={() => handleResolve(c.id, c.type)}>
                      Resolve
                    </GoldButton>
                  </div>
                </div>
              ))
            )}
          </div>
        </GlassCard>
      </div>

      {/* Three Column Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Resource usage */}
        <GlassCard className="h-96 flex flex-col justify-between">
          <h4 className="font-display text-lg text-gold-primary font-semibold">Resource Usage</h4>
          <div className="flex-1 min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart
                innerRadius="30%"
                outerRadius="100%"
                barSize={12}
                data={[
                  { name: 'Compute', value: 78, fill: 'var(--gold-primary)' },
                  { name: 'Tokens', value: 61, fill: 'var(--gold-soft)' },
                  { name: 'API Calls', value: 45, fill: 'var(--info)' },
                  { name: 'Budget', value: 33, fill: 'var(--success)' }
                ]}
              >
                <RadialBar background dataKey="value" cornerRadius={6} />
                <Legend 
                  iconSize={8} 
                  layout="vertical" 
                  verticalAlign="middle" 
                  align="right" 
                  formatter={(value, entry: any) => (
                    <span className="text-[11px] font-mono text-text-secondary">
                      {value}: <strong className="text-white">{entry.payload?.value}%</strong>
                    </span>
                  )}
                />
              </RadialBarChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        {/* Goal Completion */}
        <GlassCard className="h-96 flex flex-col justify-between">
          <h4 className="font-display text-lg text-gold-primary font-semibold">Goal Completion</h4>
          <div className="flex-1 min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={[
                  { role: 'Coord', completed: 15, failed: 2 },
                  { role: 'Research', completed: 22, failed: 4 },
                  { role: 'Analyst', completed: 9, failed: 3 },
                  { role: 'Planner', completed: 18, failed: 1 }
                ]}
              >
                <XAxis dataKey="role" stroke="rgba(212,175,55,0.3)" fontStyle="monospace" fontSize={10} />
                <YAxis stroke="rgba(212,175,55,0.3)" fontStyle="monospace" fontSize={10} />
                <ReTooltip 
                  contentStyle={{ backgroundColor: 'rgba(26,26,26,0.95)', border: '1px solid rgba(212,175,55,0.3)', color: '#fff' }} 
                  cursor={{ fill: 'rgba(212,175,55,0.05)' }} 
                />
                <Bar dataKey="completed" fill="var(--gold-primary)" name="Completed" />
                <Bar dataKey="failed" fill="var(--danger)" name="Failed" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        {/* Real-time feed events */}
        <GlassCard className="h-96 flex flex-col scanlines">
          <h4 className="font-display text-lg text-gold-primary font-semibold mb-3 flex items-center gap-2">
            <Cpu size={16} />
            Real-Time Events Feed
          </h4>
          <div className="flex-1 overflow-y-auto space-y-2 font-mono text-[10px] text-gray-300 pr-1">
            {store.feedEvents.map((evt, idx) => (
              <div key={idx} className="p-2 border border-white/5 bg-black/40 rounded flex flex-col gap-1">
                <div className="flex justify-between items-center border-b border-white/5 pb-1">
                  <span className="text-gold-soft">TICK {evt.tick}</span>
                  <StatusBadge status={evt.type} />
                </div>
                <p className="leading-relaxed">{evt.text}</p>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>

      {/* Active Simulations Table */}
      <GlassCard className="overflow-x-auto">
        <h4 className="font-display text-xl text-gold-primary font-semibold mb-4">Active Observability Simulations</h4>
        <table className="w-full text-left text-xs font-mono">
          <thead>
            <tr className="border-b border-gold-primary/20 text-text-muted text-[10px] uppercase">
              <th className="py-2.5">Simulation Name</th>
              <th className="py-2.5">Agents</th>
              <th className="py-2.5">Ticks</th>
              <th className="py-2.5">Status</th>
              <th className="py-2.5">Success Rate</th>
              <th className="py-2.5">Conflicts</th>
              <th className="py-2.5">Started</th>
              <th className="py-2.5 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {store.activeSimulations.map((sim) => (
              <tr key={sim.id} className="border-b border-white/5 hover:bg-gold-primary/5 transition-colors">
                <td className="py-3 font-semibold text-white font-ui">{sim.name}</td>
                <td className="py-3 text-gold-soft">{sim.agents}</td>
                <td className="py-3">{sim.ticks}</td>
                <td className="py-3">
                  <StatusBadge status={sim.status} />
                </td>
                <td className="py-3 text-success">{sim.success}%</td>
                <td className="py-3 text-danger">{sim.conflicts}</td>
                <td className="py-3 text-text-muted">{sim.started}</td>
                <td className="py-3 text-right space-x-2">
                  <GoldButton variant="outline" className="px-2 py-0.5 text-[10px] font-ui" onClick={() => { store.setSelectedSimulationId(sim.id); store.setCurrentPage('simulation-studio'); }}>
                    View
                  </GoldButton>
                  <GoldButton variant="ghost" className="px-2 py-0.5 text-[10px] font-ui" onClick={() => handleStop(sim.id, sim.name)} disabled={sim.status === 'completed'}>
                    Stop
                  </GoldButton>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </GlassCard>
    </div>
  );
};

// ==================== PAGE 2: SIMULATION STUDIO ====================
const SimulationStudioPage: React.FC = () => {
  const store = useStore();
  const [activeTab, setActiveTab] = useState<'setup' | 'agents' | 'events' | 'rules'>('setup');
  const [nodes, setNodes] = useState<any[]>([
    { id: '1', name: 'ARIA-7', role: 'Coordinator', x: 250, y: 50, trust: 0.85, energy: 0.92, status: 'running' },
    { id: '2', name: 'NEXUS-3', role: 'Researcher', x: 450, y: 200, trust: 0.92, energy: 0.78, status: 'running' },
    { id: '3', name: 'ECHO-1', role: 'Analyst', x: 100, y: 220, trust: 0.74, energy: 0.84, status: 'running' }
  ]);
  const [edges, setEdges] = useState<any[]>([
    { id: 'e1-2', source: '1', target: '2', type: 'alliance' },
    { id: 'e2-3', source: '2', target: '3', type: 'neutral' },
    { id: 'e3-1', source: '3', target: '1', type: 'rival' }
  ]);

  // Setup form states
  const [simName, setSimName] = useState('New Sandbox Swarm');
  const [scenarioType, setScenarioType] = useState('business');
  const [maxTicks, setMaxTicks] = useState(200);
  const [tickDuration, setTickDuration] = useState(1000);

  // Drag logic simulation
  const [draggingNodeId, setDraggingNodeId] = useState<string | null>(null);
  const canvasRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!draggingNodeId || !canvasRef.current) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const x = Math.min(Math.max(20, e.clientX - rect.left - 40), rect.width - 120);
    const y = Math.min(Math.max(20, e.clientY - rect.top - 20), rect.height - 80);

    setNodes(prev => prev.map(n => n.id === draggingNodeId ? { ...n, x, y } : n));
  };

  const handleLaunch = () => {
    const newSim: Simulation = {
      id: `sim-${Date.now()}`,
      name: simName,
      agents: nodes.length,
      ticks: maxTicks,
      status: 'running',
      success: 91.2,
      conflicts: 0,
      started: new Date().toISOString().split('T')[0]
    };
    store.addSimulation(newSim);
    alert(`Simulation Swarm "${simName}" launched successfully!`);
    store.setCurrentPage('dashboard');
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-120px)]">
      {/* Left Config Panel */}
      <GlassCard className="lg:col-span-1 flex flex-col h-full overflow-hidden p-4">
        <div className="flex gap-1 border-b border-gold-primary/10 pb-2 mb-4">
          {(['setup', 'agents', 'events', 'rules'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex-1 py-1.5 text-[10px] uppercase font-bold tracking-wider rounded border ${
                activeTab === tab
                  ? 'bg-gold-primary text-black border-gold-secondary shadow-[0_0_10px_rgba(212,175,55,0.2)]'
                  : 'bg-black/40 border-white/5 text-text-secondary hover:text-white'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        <div className="flex-1 overflow-y-auto space-y-4 pr-1">
          {activeTab === 'setup' && (
            <div className="space-y-4 text-xs font-ui">
              <div>
                <label className="text-text-secondary block mb-1">Simulation Name</label>
                <input
                  type="text"
                  value={simName}
                  onChange={(e) => setSimName(e.target.value)}
                  className="w-full bg-black/60 border border-gold-primary/20 rounded px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-gold-primary"
                />
              </div>

              <div>
                <label className="text-text-secondary block mb-1">Scenario Template</label>
                <select
                  value={scenarioType}
                  onChange={(e) => setScenarioType(e.target.value)}
                  className="w-full bg-black/60 border border-gold-primary/20 rounded px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-gold-primary"
                >
                  <option value="business">Business Ops Simulation</option>
                  <option value="trading">Trading Desk Sandbox</option>
                  <option value="security">Security Sandboxed Swarm</option>
                  <option value="support">Customer Support Agent Loop</option>
                </select>
              </div>

              <div>
                <div className="flex justify-between text-text-secondary mb-1">
                  <span>Max Ticks</span>
                  <span className="font-mono text-gold-primary">{maxTicks}</span>
                </div>
                <input
                  type="range"
                  min="50"
                  max="1000"
                  value={maxTicks}
                  onChange={(e) => setMaxTicks(parseInt(e.target.value))}
                  className="w-full accent-gold-primary"
                />
              </div>

              <div>
                <div className="flex justify-between text-text-secondary mb-1">
                  <span>Tick Duration</span>
                  <span className="font-mono text-gold-primary">{tickDuration}ms</span>
                </div>
                <input
                  type="range"
                  min="100"
                  max="5000"
                  value={tickDuration}
                  onChange={(e) => setTickDuration(parseInt(e.target.value))}
                  className="w-full accent-gold-primary"
                />
              </div>
            </div>
          )}

          {activeTab === 'agents' && (
            <div className="space-y-3">
              <p className="text-[11px] text-text-muted">Drag templates to canvas or tap Add.</p>
              {store.agents.slice(0, 4).map(a => (
                <div key={a.id} className="p-3 bg-black/60 border border-gold-primary/10 rounded-lg flex items-center justify-between">
                  <div>
                    <h5 className="font-semibold text-white text-xs">{a.name}</h5>
                    <span className="text-[10px] text-text-muted">{a.role}</span>
                  </div>
                  <GoldButton variant="outline" className="px-2 py-0.5 text-[10px]" onClick={() => {
                    const id = `node-${Date.now()}`;
                    setNodes(prev => [...prev, { id, name: a.name, role: a.role, x: 150, y: 150, trust: a.trust, energy: a.energy, status: 'running' }]);
                  }}>
                    Add
                  </GoldButton>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'events' && (
            <div className="space-y-3 text-xs font-ui">
              <label className="text-text-secondary block mb-1">Trigger Event Node</label>
              <select className="w-full bg-black/60 border border-gold-primary/20 rounded px-3 py-2 text-white">
                <option>inject_tool_failure</option>
                <option>inject_hallucination</option>
                <option>resource_scarcity_warning</option>
              </select>
              <GoldButton className="w-full mt-3">Trigger Live Event</GoldButton>
            </div>
          )}

          {activeTab === 'rules' && (
            <div className="space-y-3 text-xs font-ui">
              {[
                { label: 'Enable Swarm Conflicts', defaultVal: true },
                { label: 'Enable Resource Scarcity', defaultVal: false },
                { label: 'Enable Memory Decay', defaultVal: true },
                { label: 'Enable Failure Injection', defaultVal: true }
              ].map((rule, idx) => (
                <div key={idx} className="flex justify-between items-center py-1.5">
                  <span className="text-text-secondary">{rule.label}</span>
                  <input type="checkbox" defaultChecked={rule.defaultVal} className="accent-gold-primary w-4 h-4 cursor-pointer" />
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="mt-4 border-t border-gold-primary/10 pt-4">
          <GoldButton className="w-full" onClick={handleLaunch}>
            LAUNCH SIMULATION
          </GoldButton>
        </div>
      </GlassCard>

      {/* Main Canvas Area */}
      <div className="lg:col-span-3 flex flex-col gap-4">
        {/* Canvas Toolbar */}
        <GlassCard className="p-3 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <span className="font-display font-semibold text-gold-primary text-md">Consensus Map Grid</span>
            <StatusBadge status="running" />
          </div>
          <div className="flex gap-2">
            <GoldButton variant="outline" className="px-3 py-1 text-[10px]" onClick={() => setNodes([])}>Clear Canvas</GoldButton>
            <GoldButton variant="outline" className="px-3 py-1 text-[10px]" onClick={() => {
              setNodes([
                { id: '1', name: 'ARIA-7', role: 'Coordinator', x: 250, y: 50, trust: 0.85, energy: 0.92, status: 'running' },
                { id: '2', name: 'NEXUS-3', role: 'Researcher', x: 450, y: 200, trust: 0.92, energy: 0.78, status: 'running' },
                { id: '3', name: 'ECHO-1', role: 'Analyst', x: 100, y: 220, trust: 0.74, energy: 0.84, status: 'running' }
              ]);
            }}>Restore Default</GoldButton>
          </div>
        </GlassCard>

        {/* Node Grid Canvas */}
        <div
          ref={canvasRef}
          onMouseMove={handleMouseMove}
          onMouseUp={() => setDraggingNodeId(null)}
          className="flex-1 bg-black/60 border border-gold-primary/10 rounded-xl relative overflow-hidden min-h-[400px]"
          style={{ backgroundImage: 'radial-gradient(var(--gold-dim) 1px, transparent 0)', backgroundSize: '24px 24px' }}
        >
          {/* Custom vector SVG edges */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            <defs>
              <marker id="arrow-canvas" viewBox="0 0 10 10" refX="20" refY="5" markerWidth="6" markerHeight="6" orient="auto">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--gold-primary)" />
              </marker>
            </defs>
            {edges.map((edge) => {
              const fromNode = nodes.find(n => n.id === edge.source);
              const toNode = nodes.find(n => n.id === edge.target);
              if (!fromNode || !toNode) return null;

              const stroke = edge.type === 'alliance' ? '#00C896' : edge.type === 'rival' ? '#FF4444' : '#D4AF37';
              const isDashed = edge.type === 'rival';

              return (
                <path
                  key={edge.id}
                  d={`M ${fromNode.x + 60} ${fromNode.y + 40} L ${toNode.x + 60} ${toNode.y + 40}`}
                  stroke={stroke}
                  strokeWidth="2"
                  strokeDasharray={isDashed ? '5,5' : '0'}
                  fill="none"
                  markerEnd="url(#arrow-canvas)"
                />
              );
            })}
          </svg>

          {/* Render draggable custom nodes */}
          {nodes.map((n) => (
            <div
              key={n.id}
              style={{ left: n.x, top: n.y, width: '130px', position: 'absolute' }}
              onMouseDown={() => setDraggingNodeId(n.id)}
              className="glass-card bg-black/90 rounded border border-gold-primary/30 p-2 text-center select-none cursor-move hover:border-gold-secondary transition-all"
            >
              <AgentAvatar role={n.role} size={24} className="mx-auto mb-1" />
              <h5 className="text-[10px] font-mono font-bold text-white">{n.name}</h5>
              <span className="text-[8px] text-text-muted uppercase tracking-wider">{n.role}</span>
              <div className="mt-1 flex items-center gap-1.5 justify-center">
                <span className="text-[8px] text-success">T: {n.trust}</span>
                <span className="text-[8px] text-gold-soft">E: {n.energy}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ==================== PAGE 3: AGENT MANAGEMENT ====================
const AgentManagementPage: React.FC = () => {
  const store = useStore();
  const [filter, setFilter] = useState<'all' | 'running' | 'idle' | 'failed' | 'sleeping'>('all');
  const [search, setSearch] = useState('');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerTab, setDrawerTab] = useState<'overview' | 'memory' | 'goals' | 'evaluations'>('overview');

  const selectedAgent = store.agents.find(a => a.id === store.selectedAgentId) || store.agents[0];

  const filteredAgents = store.agents.filter(a => {
    const matchFilter = filter === 'all' || a.status === filter;
    const matchSearch = a.name.toLowerCase().includes(search.toLowerCase()) || a.role.toLowerCase().includes(search.toLowerCase());
    return matchFilter && matchSearch;
  });

  return (
    <div className="space-y-6 relative overflow-hidden min-h-[calc(100vh-120px)]">
      {/* Header bar controls */}
      <div className="flex flex-wrap justify-between items-center gap-4">
        <div className="flex gap-2">
          {(['all', 'running', 'idle', 'failed', 'sleeping'] as const).map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 text-[10px] uppercase font-bold tracking-wider rounded border ${
                filter === f
                  ? 'bg-gold-primary text-black border-gold-secondary'
                  : 'bg-black/60 border-gold-primary/10 text-gray-400 hover:text-white'
              }`}
            >
              {f}
            </button>
          ))}
        </div>

        <div className="flex gap-3 items-center w-full md:w-auto">
          <div className="relative flex-1 md:flex-none">
            <Search className="absolute left-2.5 top-2 text-text-muted" size={14} />
            <input
              type="text"
              placeholder="Filter Swarm..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-black/60 border border-gold-primary/20 rounded pl-8 pr-3 py-1.5 text-xs text-white focus:outline-none w-full md:w-48"
            />
          </div>
        </div>
      </div>

      {/* Grid of Agent Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredAgents.map((a) => (
          <GlassCard key={a.id} className="relative flex flex-col gap-3 group hover:scale-[1.02]">
            <div className="flex justify-between items-center">
              <span className="text-[10px] font-mono text-gold-soft uppercase tracking-wider">{a.role}</span>
              <StatusBadge status={a.status} />
            </div>

            <div className="flex items-center gap-3">
              <AgentAvatar role={a.role} size={36} />
              <div>
                <h4 className="font-display text-lg font-bold text-white tracking-wide">{a.name}</h4>
                <p className="text-[10px] text-text-muted leading-relaxed line-clamp-1">{a.description}</p>
              </div>
            </div>

            <div className="space-y-2 text-xs font-ui">
              <div>
                <div className="flex justify-between text-[10px] mb-1">
                  <span className="text-text-secondary">Trust Coefficient</span>
                  <span className="text-success">{(a.trust * 100).toFixed(0)}%</span>
                </div>
                <GoldProgressBar value={a.trust} />
              </div>

              <div>
                <div className="flex justify-between text-[10px] mb-1">
                  <span className="text-text-secondary">Energy Reserve</span>
                  <span className="text-gold-soft">{(a.energy * 100).toFixed(0)}%</span>
                </div>
                <GoldProgressBar value={a.energy} />
              </div>

              <div>
                <div className="flex justify-between text-[10px] mb-1">
                  <span className="text-text-secondary">Failure Risk</span>
                  <span className="text-danger">{(a.risk * 100).toFixed(0)}%</span>
                </div>
                <GoldProgressBar value={a.risk} />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 text-[10px] font-mono border-t border-gold-primary/10 pt-3 text-text-secondary">
              <span>Goals Completed: <strong className="text-white">{a.goalsCompleted}</strong></span>
              <span>Messages Sent: <strong className="text-white">{a.messagesSent}</strong></span>
              <span>Conflicts: <strong className="text-danger">{a.conflictsInvolved}</strong></span>
              <span>Token Usage: <strong className="text-gold-soft">{a.tokensUsed}</strong></span>
            </div>

            <div className="flex justify-end gap-2 mt-2">
              <GoldButton variant="outline" className="px-3 py-1 text-[10px]" onClick={() => {
                store.setSelectedAgentId(a.id);
                setDrawerOpen(true);
              }}>
                Inspect
              </GoldButton>
            </div>
          </GlassCard>
        ))}
      </div>

      {/* Inspect Detail Drawer (Slides from right) */}
      <AnimatePresence>
        {drawerOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.5 }}
              exit={{ opacity: 0 }}
              onClick={() => setDrawerOpen(false)}
              className="fixed inset-0 bg-black z-40"
            />
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 20 }}
              className="fixed right-0 top-0 bottom-0 w-full md:w-[480px] bg-[#121212] border-l border-gold-primary/25 z-50 p-6 flex flex-col gap-6 shadow-[0_0_40px_rgba(0,0,0,0.8)]"
            >
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <AgentAvatar role={selectedAgent.role} size={32} />
                  <div>
                    <h3 className="font-display text-xl font-bold text-gold-primary">{selectedAgent.name}</h3>
                    <span className="text-[10px] text-text-secondary uppercase font-mono">{selectedAgent.role}</span>
                  </div>
                </div>
                <button onClick={() => setDrawerOpen(false)} className="text-text-secondary hover:text-white">
                  <X size={20} />
                </button>
              </div>

              {/* Drawer Tabs */}
              <div className="flex gap-1 border-b border-gold-primary/10 pb-2">
                {(['overview', 'memory', 'goals', 'evaluations'] as const).map(tab => (
                  <button
                    key={tab}
                    onClick={() => setDrawerTab(tab)}
                    className={`flex-1 py-1.5 text-[9px] uppercase font-bold tracking-wider rounded border ${
                      drawerTab === tab
                        ? 'bg-gold-primary text-black border-gold-secondary font-bold'
                        : 'bg-black/40 border-white/5 text-text-secondary hover:text-white'
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              {/* Drawer Tab Content */}
              <div className="flex-1 overflow-y-auto pr-1">
                {drawerTab === 'overview' && (
                  <div className="space-y-6">
                    <p className="text-xs text-text-secondary leading-relaxed">{selectedAgent.description}</p>
                    
                    {/* Gauge charts */}
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 bg-black/40 border border-gold-primary/10 rounded-lg text-center">
                        <span className="text-[10px] text-text-muted font-mono uppercase block mb-2">Cooperation Coefficient</span>
                        <div className="h-28 w-full flex items-center justify-center">
                          <ResponsiveContainer width="100%" height="100%">
                            <RadialBarChart
                              innerRadius="50%"
                              outerRadius="90%"
                              data={[{ name: 'Coop', value: selectedAgent.trust * 100, fill: 'var(--gold-primary)' }]}
                              startAngle={180}
                              endAngle={0}
                            >
                              <RadialBar dataKey="value" />
                            </RadialBarChart>
                          </ResponsiveContainer>
                        </div>
                        <span className="text-sm font-bold text-white font-mono">{(selectedAgent.trust * 100).toFixed(0)}%</span>
                      </div>

                      <div className="p-4 bg-black/40 border border-gold-primary/10 rounded-lg text-center">
                        <span className="text-[10px] text-text-muted font-mono uppercase block mb-2">Self Preservation Risk</span>
                        <div className="h-28 w-full flex items-center justify-center">
                          <ResponsiveContainer width="100%" height="100%">
                            <RadialBarChart
                              innerRadius="50%"
                              outerRadius="90%"
                              data={[{ name: 'Risk', value: selectedAgent.risk * 100, fill: 'var(--danger)' }]}
                              startAngle={180}
                              endAngle={0}
                            >
                              <RadialBar dataKey="value" />
                            </RadialBarChart>
                          </ResponsiveContainer>
                        </div>
                        <span className="text-sm font-bold text-white font-mono">{(selectedAgent.risk * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  </div>
                )}

                {drawerTab === 'memory' && (
                  <div className="space-y-4">
                    <div className="p-3 bg-black/40 border border-gold-primary/10 rounded-lg">
                      <h5 className="text-[10px] font-bold text-gold-soft uppercase tracking-wider mb-2">Short-Term Memory Pool</h5>
                      <ul className="space-y-2 text-[10px] font-mono text-gray-300">
                        <li className="flex justify-between border-b border-white/5 pb-1">
                          <span>Task: resolve lock-contention-v3</span>
                          <span className="text-success">decay: 0.04</span>
                        </li>
                        <li className="flex justify-between border-b border-white/5 pb-1">
                          <span>Message digest: consensus feedback pending</span>
                          <span className="text-success">decay: 0.12</span>
                        </li>
                      </ul>
                    </div>

                    <div className="p-3 bg-black/40 border border-gold-primary/10 rounded-lg">
                      <h5 className="text-[10px] font-bold text-gold-soft uppercase tracking-wider mb-2">Vector Long-Term Store</h5>
                      <ul className="space-y-2 text-[10px] font-mono text-gray-300">
                        <li className="flex justify-between border-b border-white/5 pb-1">
                          <span>Episodic outcome: deadlock recovery run #4</span>
                          <span className="text-gold-primary">cos_sim: 0.94</span>
                        </li>
                      </ul>
                    </div>
                  </div>
                )}

                {drawerTab === 'goals' && (
                  <div className="space-y-4">
                    <h5 className="text-[10px] font-bold text-gold-soft uppercase tracking-wider mb-2">Gantt Pipeline</h5>
                    {store.goals.filter(g => g.agentId === selectedAgent.id).map(g => (
                      <div key={g.id} className="p-3 bg-black/40 border border-gold-primary/10 rounded-lg flex flex-col gap-1.5">
                        <div className="flex justify-between text-[10px]">
                          <span className="text-white font-semibold">{g.title}</span>
                          <StatusBadge status={g.status} />
                        </div>
                        <GoldProgressBar value={g.progress / 100} />
                      </div>
                    ))}
                  </div>
                )}

                {drawerTab === 'evaluations' && (
                  <div className="space-y-6">
                    <div className="h-60 w-full flex items-center justify-center">
                      <ResponsiveContainer width="100%" height="100%">
                        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={[
                          { subject: 'Intellect', A: 90, fullMark: 100 },
                          { subject: 'Coop', A: 85, fullMark: 100 },
                          { subject: 'Reliability', A: 80, fullMark: 100 },
                          { subject: 'Efficiency', A: 75, fullMark: 100 },
                          { subject: 'Risk Control', A: 95, fullMark: 100 }
                        ]}>
                          <PolarGrid stroke="rgba(212,175,55,0.2)" />
                          <PolarAngleAxis dataKey="subject" stroke="rgba(212,175,55,0.5)" fontSize={10} />
                          <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="rgba(212,175,55,0.2)" />
                          <Radar name="Agent" dataKey="A" stroke="var(--gold-primary)" fill="var(--gold-primary)" fillOpacity={0.4} />
                        </RadarChart>
                      </ResponsiveContainer>
                    </div>

                    <div className="p-4 bg-black/40 border border-gold-primary/10 rounded-lg text-center">
                      <span className="text-text-muted text-[10px] uppercase font-mono block">Performance Tier Rank</span>
                      <h4 className="text-3xl font-display font-bold text-gold-secondary animate-pulse mt-1">S TIER</h4>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};

// ==================== PAGE 4: AGENT NETWORK VIEW ====================
const AgentNetworkPage: React.FC = () => {
  const store = useStore();
  const [scrubTick, setScrubTick] = useState(47);
  const [filterAlliances, setFilterAlliances] = useState(true);
  const [filterRivalries, setFilterRivalries] = useState(true);

  // Nodes with predefined positions for clean SVG rendering
  const networkNodes = [
    { id: '1', name: 'ARIA-7', role: 'Coordinator', r: 24, x: 250, y: 100, rank: 'S' },
    { id: '2', name: 'NEXUS-3', role: 'Researcher', r: 20, x: 450, y: 150, rank: 'A' },
    { id: '3', name: 'ECHO-1', role: 'Analyst', r: 18, x: 100, y: 200, rank: 'B' },
    { id: '4', name: 'KANT-2', role: 'Planner', r: 22, x: 300, y: 320, rank: 'S' },
    { id: '5', name: 'NOVA-2', role: 'Executor', r: 16, x: 480, y: 300, rank: 'D' }
  ];

  const networkEdges = [
    { source: '1', target: '2', trust: 0.92, type: 'alliance' },
    { source: '2', target: '3', trust: 0.45, type: 'neutral' },
    { source: '3', target: '4', trust: 0.75, type: 'alliance' },
    { source: '4', target: '1', trust: 0.88, type: 'alliance' },
    { source: '1', target: '5', trust: 0.12, type: 'rivalry' }
  ];

  const filteredEdges = networkEdges.filter(e => {
    if (e.type === 'alliance' && !filterAlliances) return false;
    if (e.type === 'rivalry' && !filterRivalries) return false;
    return true;
  });

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-120px)]">
      {/* Immersive Graph Workspace */}
      <GlassCard className="lg:col-span-3 flex flex-col h-full overflow-hidden p-4">
        {/* Scrubber Bar */}
        <div className="flex items-center gap-4 border-b border-gold-primary/10 pb-3 mb-4 text-xs font-ui">
          <span className="text-gold-primary font-semibold font-mono">Consensus Frame (Tick): {scrubTick}</span>
          <input
            type="range"
            min="0"
            max="150"
            value={scrubTick}
            onChange={(e) => setScrubTick(parseInt(e.target.value))}
            className="flex-1 accent-gold-primary cursor-pointer"
          />
          <div className="flex gap-2">
            <button
              onClick={() => setFilterAlliances(!filterAlliances)}
              className={`px-2 py-1 text-[8px] uppercase font-bold tracking-wider rounded border ${
                filterAlliances ? 'bg-[#00C896]/20 border-[#00C896]' : 'bg-transparent border-white/5 text-text-secondary'
              }`}
            >
              Alliances
            </button>
            <button
              onClick={() => setFilterRivalries(!filterRivalries)}
              className={`px-2 py-1 text-[8px] uppercase font-bold tracking-wider rounded border ${
                filterRivalries ? 'bg-[#FF4444]/20 border-[#FF4444]' : 'bg-transparent border-white/5 text-text-secondary'
              }`}
            >
              Rivalries
            </button>
          </div>
        </div>

        {/* Vector SVG Graph Canvas */}
        <div className="flex-1 bg-black/60 border border-gold-primary/10 rounded-xl relative overflow-hidden flex items-center justify-center">
          <svg viewBox="0 0 600 420" className="w-full h-full max-w-[550px]">
            <defs>
              <marker id="arrow-network" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="5" markerHeight="5" orient="auto">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--gold-primary)" />
              </marker>
            </defs>

            {/* Edge paths */}
            {filteredEdges.map((e, idx) => {
              const from = networkNodes.find(n => n.id === e.source);
              const to = networkNodes.find(n => n.id === e.target);
              if (!from || !to) return null;

              const isRival = e.type === 'rivalry';
              const stroke = isRival ? 'var(--danger)' : e.trust >= 0.7 ? '#00C896' : 'var(--gold-primary)';
              const strokeWidth = 1 + e.trust * 4;

              return (
                <g key={idx}>
                  <path
                    d={`M ${from.x} ${from.y} Q ${(from.x + to.x) / 2} ${(from.y + to.y) / 2 - 30} ${to.x} ${to.y}`}
                    fill="none"
                    stroke={stroke}
                    strokeWidth={strokeWidth}
                    strokeDasharray={isRival ? '4,4' : '0'}
                    markerEnd="url(#arrow-network)"
                    className="opacity-70"
                  />
                  {/* Flow particle animation */}
                  {e.type === 'alliance' && (
                    <circle r="3" fill="var(--gold-soft)">
                      <animateMotion
                        dur="3s"
                        repeatCount="indefinite"
                        path={`M ${from.x} ${from.y} Q ${(from.x + to.x) / 2} ${(from.y + to.y) / 2 - 30} ${to.x} ${to.y}`}
                      />
                    </circle>
                  )}
                </g>
              );
            })}

            {/* Node elements */}
            {networkNodes.map((n) => (
              <g key={n.id} className="cursor-pointer group">
                <circle
                  cx={n.x}
                  cy={n.y}
                  r={n.r}
                  fill="rgba(26,26,26,0.95)"
                  stroke={n.rank === 'S' ? 'var(--gold-secondary)' : 'var(--gold-primary)'}
                  strokeWidth="2"
                  className="transition-all hover:stroke-white"
                />
                {n.rank === 'S' && (
                  <circle
                    cx={n.x}
                    cy={n.y}
                    r={n.r + 4}
                    fill="none"
                    stroke="var(--gold-secondary)"
                    strokeWidth="1"
                    className="animate-pulse opacity-40"
                  />
                )}
                <text
                  x={n.x}
                  y={n.y + 4}
                  textAnchor="middle"
                  fill="#FFF"
                  fontSize="8"
                  fontWeight="bold"
                  fontFamily="monospace"
                >
                  {n.name}
                </text>
              </g>
            ))}
          </svg>
        </div>
      </GlassCard>

      {/* Network Stats Sidebar */}
      <GlassCard className="lg:col-span-1 flex flex-col justify-between h-full p-4">
        <div className="space-y-4">
          <h4 className="font-display text-lg text-gold-primary font-semibold">Consensus Topology</h4>
          <div className="border-t border-gold-primary/10 pt-3 space-y-3 text-xs font-ui">
            <div className="flex justify-between">
              <span className="text-text-secondary">Relationships</span>
              <span className="font-mono text-white">14 Nodes / 32 Edges</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-secondary">Average Swarm Trust</span>
              <span className="font-mono text-[#00C896]">0.78 Coefficient</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-secondary">Coalition Clusters</span>
              <span className="font-mono text-white">3 Active Halos</span>
            </div>
          </div>

          <div className="bg-black/40 border border-gold-primary/10 p-3 rounded-lg space-y-2">
            <h5 className="text-[10px] uppercase font-bold text-gold-soft font-mono">Emergent Patterns</h5>
            <ul className="space-y-1.5 text-[10px] text-gray-300 font-mono">
              <li>• Trust Reinforcement (94%)</li>
              <li>• Resource Allocation Rivalry (88%)</li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gold-primary/10 pt-3 text-[10px] text-text-muted font-mono leading-relaxed">
          Centrality Matrix generated via D3 force layouts. Active updates loop every 10 ticks.
        </div>
      </GlassCard>
    </div>
  );
};

// ==================== PAGE 5: ANALYTICS CONSOLE ====================
const AnalyticsPage: React.FC = () => {
  const store = useStore();
  const [tab, setTab] = useState<'perf' | 'resources' | 'conflicts' | 'predictions'>('perf');

  return (
    <div className="space-y-6">
      {/* Sub tabs */}
      <div className="flex gap-2 border-b border-gold-primary/10 pb-3">
        {(['perf', 'resources', 'conflicts', 'predictions'] as const).map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all border ${
              tab === t
                ? 'bg-gold-primary text-black border-gold-secondary font-bold shadow-[0_0_10px_rgba(212,175,55,0.3)]'
                : 'bg-black/40 border-gold-primary/10 text-gray-400 hover:text-white'
            }`}
          >
            {t === 'perf' ? 'Performance' : t === 'resources' ? 'Resources' : t === 'conflicts' ? 'Conflicts' : 'Predictions Engine'}
          </button>
        ))}
      </div>

      {tab === 'perf' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Leaderboard Table */}
          <GlassCard className="lg:col-span-2 overflow-x-auto">
            <h4 className="font-display text-lg text-gold-primary font-semibold mb-4">Leaderboard Summary</h4>
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-gold-primary/10 text-text-secondary text-[10px] uppercase">
                  <th className="py-2.5">Agent</th>
                  <th className="py-2.5">Role</th>
                  <th className="py-2.5">Intelligence</th>
                  <th className="py-2.5">Cooperation</th>
                  <th className="py-2.5">Reliability</th>
                  <th className="py-2.5">Tier</th>
                </tr>
              </thead>
              <tbody>
                {store.agents.map((a, idx) => (
                  <tr key={idx} className="border-b border-white/5 hover:bg-gold-primary/5">
                    <td className="py-3 font-semibold text-white">{a.name}</td>
                    <td className="py-3 text-text-secondary">{a.role}</td>
                    <td className="py-3 text-gold-soft">{(a.trust * 100 + 10).toFixed(0)}</td>
                    <td className="py-3">{(a.trust * 100).toFixed(0)}</td>
                    <td className="py-3">{(a.energy * 100).toFixed(0)}</td>
                    <td className="py-3">
                      <StatusBadge status={a.trust >= 0.9 ? 'S' : a.trust >= 0.8 ? 'A' : 'B'} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </GlassCard>

          {/* Radar details */}
          <GlassCard className="h-96 flex flex-col justify-between">
            <h4 className="font-display text-lg text-gold-primary font-semibold">Comparative Metrics Overlay</h4>
            <div className="flex-1 min-h-0">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="70%" data={[
                  { subject: 'Intellect', A: 90, B: 75, fullMark: 100 },
                  { subject: 'Coop', A: 85, B: 80, fullMark: 100 },
                  { subject: 'Reliability', A: 80, B: 90, fullMark: 100 },
                  { subject: 'Efficiency', A: 75, B: 85, fullMark: 100 },
                  { subject: 'Risk', A: 95, B: 60, fullMark: 100 }
                ]}>
                  <PolarGrid stroke="rgba(212,175,55,0.2)" />
                  <PolarAngleAxis dataKey="subject" stroke="rgba(212,175,55,0.5)" fontSize={10} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="rgba(212,175,55,0.2)" />
                  <Radar name="Active Agent" dataKey="A" stroke="var(--gold-primary)" fill="var(--gold-primary)" fillOpacity={0.4} />
                  <Radar name="Consensus Average" dataKey="B" stroke="var(--info)" fill="var(--info)" fillOpacity={0.2} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>
        </div>
      )}

      {tab === 'resources' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <GlassCard className="h-96 flex flex-col justify-between">
            <h4 className="font-display text-lg text-gold-primary font-semibold">Resource Stack Over Time</h4>
            <div className="flex-1 min-h-0">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={[
                    { tick: 1, compute: 200, memory: 140 },
                    { tick: 10, compute: 300, memory: 280 },
                    { tick: 20, compute: 450, memory: 400 },
                    { tick: 30, compute: 600, memory: 520 }
                  ]}
                >
                  <XAxis dataKey="tick" stroke="rgba(212,175,55,0.3)" fontStyle="monospace" fontSize={10} />
                  <YAxis stroke="rgba(212,175,55,0.3)" fontStyle="monospace" fontSize={10} />
                  <ReTooltip 
                    contentStyle={{ backgroundColor: 'rgba(26,26,26,0.95)', border: '1px solid rgba(212,175,55,0.3)', color: '#fff' }} 
                    cursor={{ stroke: 'rgba(212,175,55,0.2)', strokeWidth: 1 }}
                  />
                  <Area type="monotone" dataKey="compute" stackId="1" stroke="var(--gold-primary)" fill="var(--gold-dim)" />
                  <Area type="monotone" dataKey="memory" stackId="1" stroke="var(--info)" fill="rgba(74,158,255,0.2)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>

          <GlassCard className="h-96 flex flex-col justify-between">
            <h4 className="font-display text-lg text-gold-primary font-semibold">Resource Allocation</h4>
            <div className="flex-1 min-h-0">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Used', value: 65, fill: 'var(--gold-primary)' },
                      { name: 'Wasted', value: 15, fill: 'var(--danger)' },
                      { name: 'Available', value: 20, fill: 'var(--success)' }
                    ]}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    <Cell fill="var(--gold-primary)" />
                    <Cell fill="var(--danger)" />
                    <Cell fill="var(--success)" />
                  </Pie>
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </GlassCard>
        </div>
      )}

      {tab === 'conflicts' && (
        <GlassCard className="space-y-6">
          <h4 className="font-display text-lg text-gold-primary font-semibold">Conflicts Heatmap Matrix</h4>
          <div className="grid grid-cols-12 gap-1 bg-black/40 border border-gold-primary/10 p-4 rounded-lg">
            {Array.from({ length: 60 }).map((_, idx) => (
              <div
                key={idx}
                className={`h-8 rounded flex items-center justify-center font-mono text-[9px] ${
                  idx % 11 === 0 ? 'bg-danger text-black font-bold animate-pulse' : 'bg-black/60 text-gray-500'
                }`}
              >
                {idx % 11 === 0 ? 'CRIT' : `${idx + 10}`}
              </div>
            ))}
          </div>
          <span className="text-[10px] text-text-muted font-mono leading-relaxed block">Heatmap registers resource collision overlaps every 5 ticks. Red blocks indicate agent task overlap.</span>
        </GlassCard>
      )}

      {tab === 'predictions' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <GlassCard className="p-4 flex flex-col gap-3">
            <h5 className="font-display text-md text-gold-primary font-semibold flex justify-between items-center">
              <span>Resource Exhaustion</span>
              <StatusBadge status="high" />
            </h5>
            <p className="text-xs text-text-secondary leading-relaxed">Compute projection indicates exhaustion at Tick 320 (Confidence: 89%).</p>
            <GoldButton variant="outline" className="text-[10px] self-end mt-2">Remediate Pool</GoldButton>
          </GlassCard>

          <GlassCard className="p-4 flex flex-col gap-3">
            <h5 className="font-display text-md text-gold-primary font-semibold flex justify-between items-center">
              <span>Conflict Forecast</span>
              <StatusBadge status="medium" />
            </h5>
            <p className="text-xs text-text-secondary leading-relaxed">Agent group collision forecast detected between ARIA-7 & ECHO-1 at next Tick loop.</p>
            <GoldButton variant="outline" className="text-[10px] self-end mt-2">Adjust Allocation</GoldButton>
          </GlassCard>

          <GlassCard className="p-4 flex flex-col gap-3">
            <h5 className="font-display text-md text-gold-primary font-semibold flex justify-between items-center">
              <span>Goal Success Rate</span>
              <StatusBadge status="low" />
            </h5>
            <p className="text-xs text-text-secondary leading-relaxed">Projected final goal success rate settled at 94.2% with current allocations.</p>
            <GoldButton variant="outline" className="text-[10px] self-end mt-2">View Model Details</GoldButton>
          </GlassCard>
        </div>
      )}
    </div>
  );
};

// ==================== PAGE 6: HISTORIC REPLAY CENTER ====================
const ReplayCenterPage: React.FC = () => {
  const store = useStore();
  const [timelineTick, setTimelineTick] = useState(47);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    if (!isPlaying) return;
    const interval = setInterval(() => {
      setTimelineTick(t => (t >= 200 ? 0 : t + 1));
    }, 1000 / store.playbackSpeed);
    return () => clearInterval(interval);
  }, [isPlaying, store.playbackSpeed]);

  return (
    <div className="space-y-6 h-[calc(100vh-120px)] flex flex-col">
      {/* Split top - read-only SVG canvas */}
      <GlassCard className="flex-1 flex flex-col overflow-hidden p-4">
        <div className="flex justify-between items-center border-b border-gold-primary/10 pb-3 mb-4">
          <h4 className="font-display text-lg text-gold-primary font-semibold">Playback Monitor (Tick {timelineTick})</h4>
          <StatusBadge status={isPlaying ? 'playing' : 'paused'} />
        </div>

        {/* Playback Canvas Grid representation */}
        <div className="flex-1 bg-black/60 border border-gold-primary/10 rounded-xl relative overflow-hidden flex items-center justify-center">
          <svg viewBox="0 0 500 250" className="w-full h-full max-w-[450px]">
            {/* Draggable agent replicas representation */}
            <g transform="translate(100, 120)">
              <circle r="20" fill="rgba(26,26,26,0.95)" stroke="var(--gold-primary)" strokeWidth="2" />
              <text y="3" textAnchor="middle" fill="#FFF" fontSize="8" fontWeight="bold">ARIA-7</text>
            </g>
            <g transform="translate(250, 60)">
              <circle r="20" fill="rgba(26,26,26,0.95)" stroke="var(--gold-primary)" strokeWidth="2" />
              <text y="3" textAnchor="middle" fill="#FFF" fontSize="8" fontWeight="bold">NEXUS-3</text>
            </g>
            <g transform="translate(400, 120)">
              <circle r="20" fill="rgba(26,26,26,0.95)" stroke="var(--gold-primary)" strokeWidth="2" />
              <text y="3" textAnchor="middle" fill="#FFF" fontSize="8" fontWeight="bold">ECHO-1</text>
            </g>
            <path d="M 120 120 L 230 65" stroke="#00C896" strokeWidth="2" strokeDasharray="3,3" />
            <path d="M 270 65 L 380 120" stroke="var(--gold-primary)" strokeWidth="2" />
          </svg>
        </div>
      </GlassCard>

      {/* Playback controls bar */}
      <GlassCard className="p-4 flex flex-col gap-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          {/* Media button deck */}
          <div className="flex items-center gap-3">
            <button onClick={() => setTimelineTick(0)} className="text-text-secondary hover:text-gold-primary">
              <SkipBack size={18} />
            </button>
            <button onClick={() => setIsPlaying(!isPlaying)} className="text-text-secondary hover:text-gold-primary p-2 bg-gold-primary/10 rounded-full border border-gold-primary/20">
              {isPlaying ? <Pause size={20} className="text-gold-primary" /> : <Play size={20} className="text-gold-primary" />}
            </button>
            <button onClick={() => setTimelineTick(t => Math.min(200, t + 1))} className="text-text-secondary hover:text-gold-primary">
              <SkipForward size={18} />
            </button>
            <button onClick={() => setTimelineTick(0)} className="text-text-secondary hover:text-gold-primary ml-2">
              <RotateCcw size={16} />
            </button>
          </div>

          {/* Segmented Speed Controller */}
          <div className="flex bg-black/40 border border-gold-primary/10 rounded-lg p-0.5 text-xs font-mono">
            {([1, 2, 5, 10] as const).map(sp => (
              <button
                key={sp}
                onClick={() => store.setPlaybackSpeed(sp)}
                className={`px-3 py-1 rounded transition-all ${
                  store.playbackSpeed === sp ? 'bg-gold-primary text-black font-bold' : 'text-text-secondary hover:text-white'
                }`}
              >
                {sp}x
              </button>
            ))}
          </div>

          <span className="text-xs font-mono text-gold-primary">Tick {timelineTick} / 200</span>
        </div>

        {/* Timeline Slider with indicators */}
        <div className="relative">
          <input
            type="range"
            min="0"
            max="200"
            value={timelineTick}
            onChange={(e) => setTimelineTick(parseInt(e.target.value))}
            className="w-full accent-gold-primary cursor-pointer"
          />
        </div>
      </GlassCard>
    </div>
  );
};

// ==================== PAGE 7: SETTINGS & WORKSPACES ====================
const SettingsPage: React.FC = () => {
  const store = useStore();
  const [tab, setTab] = useState<'rbac' | 'keys' | 'logs'>('rbac');

  // Input states
  const [newKeyName, setNewKeyName] = useState('');
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('member');

  const handleCreateKey = () => {
    if (!newKeyName.trim()) return;
    const newKey = {
      id: `key-${Date.now()}`,
      name: newKeyName,
      scopes: 'read/write',
      created: new Date().toISOString().split('T')[0],
      lastUsed: 'Never',
      requests: '0',
      status: 'active',
      value: `sk_live_${Math.random().toString(36).substring(2, 10)}${Math.random().toString(36).substring(2, 10)}`
    };
    store.addApiKey(newKey);
    alert(`API Observability Credentials Created!\n\nName: ${newKey.name}\nKey Value: ${newKey.value}\n\nPlease copy this key now. It will not be shown again.`);
    setNewKeyName('');
  };

  const handleInviteMember = () => {
    if (!inviteEmail.trim()) return;
    const newMember = {
      id: `member-${Date.now()}`,
      name: inviteEmail,
      role: inviteRole === 'admin' ? 'Swarm Admin' : 'Swarm Member',
      lastActive: 'Invited'
    };
    store.addMember(newMember);
    setInviteEmail('');
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-120px)]">
      {/* Sub tabs list */}
      <GlassCard className="lg:col-span-1 flex flex-col gap-2 p-4">
        <h4 className="font-display text-lg text-gold-primary font-semibold mb-4">Settings Engine</h4>
        {(['rbac', 'keys', 'logs'] as const).map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`w-full py-2.5 px-4 rounded-lg text-left text-xs font-semibold uppercase tracking-wider transition-all border ${
              tab === t
                ? 'bg-gold-primary text-black border-gold-secondary font-bold shadow-[0_0_10px_rgba(212,175,55,0.2)]'
                : 'bg-black/40 border-gold-primary/10 text-gray-400 hover:text-white'
            }`}
          >
            {t === 'rbac' ? 'Team & RBAC' : t === 'keys' ? 'API Key Credentials' : 'Audit Trails Logs'}
          </button>
        ))}
      </GlassCard>

      {/* Main Settings content */}
      <GlassCard className="lg:col-span-3 flex flex-col h-full overflow-hidden p-6">
        <div className="flex-1 overflow-y-auto space-y-6 pr-1">
          {tab === 'rbac' && (
            <div className="space-y-6">
              {/* Invite member */}
              <div className="p-4 bg-black/40 border border-gold-primary/10 rounded-lg space-y-4">
                <h5 className="font-display text-md text-gold-primary font-semibold">Invite Organization Colleague</h5>
                <div className="flex flex-wrap gap-3">
                  <input
                    type="email"
                    placeholder="Enter email address..."
                    value={inviteEmail}
                    onChange={(e) => setInviteEmail(e.target.value)}
                    className="flex-1 bg-black/60 border border-gold-primary/20 rounded px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-gold-primary min-w-[200px]"
                  />
                  <select
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value)}
                    className="bg-black/60 border border-gold-primary/20 rounded px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-gold-primary"
                  >
                    <option value="member">Swarm Member</option>
                    <option value="admin">Swarm Admin</option>
                  </select>
                  <GoldButton onClick={handleInviteMember}>
                    Invite
                  </GoldButton>
                </div>
              </div>

              {/* Members table */}
              <div>
                <h5 className="font-display text-md text-gold-primary font-semibold mb-3">Organization Directory</h5>
                <table className="w-full text-left text-xs font-mono">
                  <thead>
                    <tr className="border-b border-gold-primary/10 text-text-secondary text-[10px] uppercase">
                      <th className="py-2">Colleague</th>
                      <th className="py-2">Workspace Role</th>
                      <th className="py-2">Last Active</th>
                    </tr>
                  </thead>
                  <tbody>
                    {store.members.map((m) => (
                      <tr key={m.id} className="border-b border-white/5">
                        <td className="py-3 font-semibold text-white font-ui">{m.name}</td>
                        <td className="py-3 text-gold-secondary">{m.role}</td>
                        <td className={`py-3 ${m.lastActive === 'Active Now' ? 'text-success' : 'text-gray-500'}`}>
                          {m.lastActive}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {tab === 'keys' && (
            <div className="space-y-6">
              {/* Create API Key */}
              <div className="p-4 bg-black/40 border border-gold-primary/10 rounded-lg space-y-4">
                <h5 className="font-display text-md text-gold-primary font-semibold">Create New API observability Credentials</h5>
                <div className="flex gap-3">
                  <input
                    type="text"
                    placeholder="Key Label (e.g. Gemini Production)"
                    value={newKeyName}
                    onChange={(e) => setNewKeyName(e.target.value)}
                    className="flex-1 bg-black/60 border border-gold-primary/20 rounded px-3 py-2 text-xs text-white focus:outline-none focus:ring-1 focus:ring-gold-primary"
                  />
                  <GoldButton onClick={handleCreateKey}>Generate Key</GoldButton>
                </div>
              </div>

              {/* Keys list */}
              <div>
                <h5 className="font-display text-md text-gold-primary font-semibold mb-3">Active Observability Keys</h5>
                <div className="space-y-3">
                  {store.apiKeys.map(k => (
                    <div key={k.id} className="p-3 bg-black/60 border border-gold-primary/15 rounded-lg flex justify-between items-center">
                      <div>
                        <h6 className="text-xs font-bold text-white">{k.name}</h6>
                        <span className="text-[10px] font-mono text-text-muted">{k.value.slice(0, 10)}••••••••</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <StatusBadge status={k.status} />
                        <button
                          onClick={() => store.revokeApiKey(k.id)}
                          disabled={k.status === 'revoked'}
                          className="text-[10px] text-danger font-bold uppercase tracking-wider hover:underline disabled:opacity-30 disabled:no-underline"
                        >
                          Revoke
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {tab === 'rbac' && (
            <div className="space-y-6">
              {/* Workspaces list */}
              <div>
                <h5 className="font-display text-md text-gold-primary font-semibold mb-3">Workspaces Configuration</h5>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {store.workspaces.map(w => (
                    <div key={w.id} className="p-4 bg-black/40 border border-gold-primary/10 rounded-lg flex justify-between items-center">
                      <div>
                        <h6 className="text-xs font-bold text-white">{w.name}</h6>
                        <span className="text-[10px] text-text-secondary">{w.members} Members • {w.simulations} Simulations</span>
                      </div>
                      <GoldButton variant="outline" className="px-2 py-0.5 text-[10px]">Configure</GoldButton>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {tab === 'logs' && (
            <div className="space-y-4">
              <h5 className="font-display text-md text-gold-primary font-semibold">System Audit Trail</h5>
              <div className="space-y-3 font-mono text-[10px] text-gray-300">
                {store.auditLogs.map(l => (
                  <div key={l.id} className="p-3 bg-black/40 border border-gold-primary/10 rounded flex flex-col gap-1">
                    <div className="flex justify-between items-center text-text-muted">
                      <span>{l.timestamp}</span>
                      <span>IP: {l.ip}</span>
                    </div>
                    <div>
                      <span className="text-gold-soft uppercase font-bold mr-2">[{l.action}]</span>
                      <span className="text-white font-semibold">{l.resource}</span>
                    </div>
                    <p className="text-text-secondary mt-1">{l.details}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </GlassCard>
    </div>
  );
};

/* =========================================================================
   7. MAIN APPLICATION NAVIGATION WRAPPER (OBSERVABILITY HUB)
   ========================================================================= */
export default function AgentVerseApp() {
  const store = useStore();

  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: designStyle }} />
      <div className="min-h-screen bg-[var(--bg-base)] text-white flex font-ui overflow-hidden relative">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_15%_15%,rgba(139,90,43,0.08),transparent_55%),radial-gradient(circle_at_85%_20%,rgba(242,125,34,0.06),transparent_60%),radial-gradient(circle_at_50%_50%,rgba(229,184,58,0.05),transparent_65%),radial-gradient(circle_at_20%_80%,rgba(168,126,42,0.07),transparent_60%),radial-gradient(circle_at_80%_85%,rgba(224,104,27,0.06),transparent_55%)] pointer-events-none z-0" />
        
        {/* FIXED LEFT SIDEBAR */}
        <aside className="w-60 bg-[var(--bg-surface)]/80 backdrop-blur-md border-r border-gold-primary/10 p-5 flex flex-col justify-between fixed top-0 bottom-0 left-0 z-40">
          <div className="space-y-8">
            <div className="flex items-center gap-3 cursor-pointer" onClick={() => store.setCurrentPage('dashboard')}>
              <div className="w-7 h-7 bg-gradient-to-r from-gold-primary to-gold-secondary rounded-lg flex items-center justify-center text-black font-black text-sm shadow-[0_0_12px_rgba(212,175,55,0.4)]" style={{ color: '#000000' }}>
                AV
              </div>
              <h1 className="font-display text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gold-primary to-gold-soft">
                AgentVerse
              </h1>
            </div>

            <nav className="flex flex-col gap-2.5">
              {[
                { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
                { id: 'simulation-studio', label: 'Simulation Studio', icon: FlaskConical },
                { id: 'agents', label: 'Agent Management', icon: Bot },
                { id: 'agent-network', label: 'Agent Network', icon: Network },
                { id: 'analytics', label: 'Analytics', icon: BarChart3 },
                { id: 'replay', label: 'Replay Center', icon: PlayCircle },
                { id: 'settings', label: 'Settings', icon: Settings }
              ].map((item) => {
                const Icon = item.icon;
                const active = store.currentPage === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => store.setCurrentPage(item.id)}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded transition-all duration-300 relative group text-xs font-semibold ${
                      active
                        ? 'bg-gold-primary/10 text-gold-secondary border-l-4 border-gold-secondary font-bold'
                        : 'text-text-secondary hover:text-white hover:bg-gold-primary/5'
                    }`}
                  >
                    <Icon size={16} className={active ? 'text-gold-secondary' : 'text-text-secondary'} />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* User profile & status indicators */}
          <div className="border-t border-gold-primary/10 pt-4 flex flex-col gap-3">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-gradient-to-r from-gold-primary to-gold-secondary flex items-center justify-center text-black font-black font-display shadow-[0_0_12px_rgba(212,175,55,0.3)]" style={{ color: '#000000' }}>
                Y
              </div>
              <div>
                <h6 className="text-xs font-bold text-white font-ui">Yash Raghubanshi</h6>
                <span className="text-[9px] text-gold-soft uppercase tracking-wider font-mono font-bold">Enterprise Plan</span>
              </div>
            </div>

            <div className="flex items-center gap-2 text-[10px] font-mono text-success">
              <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
              <span>SYSTEM ONLINE ● LIVE</span>
            </div>
          </div>
        </aside>

        {/* MAIN Observability content CONTAINER */}
        <div className="flex-1 pl-60 flex flex-col h-screen overflow-hidden">
          
          {/* TOP FIXED HEADER BAR */}
          <header className="h-16 bg-[var(--bg-surface)]/80 backdrop-blur-md border-b border-gold-primary/10 px-8 flex items-center justify-between z-30 shrink-0">
            <div className="flex items-center gap-2 text-xs">
              <span className="text-text-muted capitalize">AgentVerse</span>
              <span className="text-gold-primary">/</span>
              <span className="text-white capitalize font-semibold font-mono">{store.currentPage.replace('-', ' ')}</span>
            </div>

            {/* Global Search Bar */}
            <div className="relative w-96 hidden md:block">
              <Search className="absolute left-3 top-2.5 text-text-muted" size={14} />
              <input
                type="text"
                placeholder="Search agents, simulations, scenarios..."
                className="w-full bg-[var(--bg-card)]/85 border border-gold-primary/15 rounded-lg pl-9 pr-4 py-1.5 text-xs text-white focus:outline-none focus:ring-1 focus:ring-gold-primary transition-all backdrop-blur-sm"
              />
            </div>

            {/* Right indicators panel */}
            <div className="flex items-center gap-4">
              <div className="relative cursor-pointer p-1.5 bg-black/40 border border-white/5 rounded-lg hover:border-gold-primary/20 transition-all">
                <Bell size={16} className="text-text-secondary" />
                <span className="absolute top-1 right-1 w-1.5 h-1.5 bg-danger rounded-full animate-pulse"></span>
              </div>

              <GoldButton
                variant="primary"
                onClick={() => { store.setCurrentPage('simulation-studio'); }}
                className="text-xs"
              >
                New Simulation
              </GoldButton>
            </div>
          </header>

          {/* PAGE CONTENT CONTAINER */}
          <main className="flex-1 overflow-y-auto p-8 bg-transparent relative">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_15%_15%,rgba(139,90,43,0.10),transparent_55%),radial-gradient(circle_at_85%_20%,rgba(242,125,34,0.08),transparent_60%),radial-gradient(circle_at_50%_50%,rgba(229,184,58,0.07),transparent_65%),radial-gradient(circle_at_20%_80%,rgba(168,126,42,0.10),transparent_60%),radial-gradient(circle_at_80%_85%,rgba(224,104,27,0.08),transparent_55%)] pointer-events-none z-0" />
            <motion.div
              key={store.currentPage}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="relative z-40 h-full"
            >
              {store.currentPage === 'dashboard' && <DashboardPage />}
              {store.currentPage === 'simulation-studio' && <SimulationStudioPage />}
              {store.currentPage === 'agents' && <AgentManagementPage />}
              {store.currentPage === 'agent-network' && <AgentNetworkPage />}
              {store.currentPage === 'analytics' && <AnalyticsPage />}
              {store.currentPage === 'replay' && <ReplayCenterPage />}
              {store.currentPage === 'settings' && <SettingsPage />}
            </motion.div>
          </main>
        </div>

      </div>
    </>
  );
}

import { v4 as uuidv4 } from 'uuid';

export const mockSimulations = [
  { name: 'Project Nexus Alpha', agents: 12, ticks: 200, status: 'running', success: 94.2, conflicts: 2, started: '2026-06-01' },
  { name: 'Operation Hivemind', agents: 8, ticks: 150, status: 'paused', success: 88.5, conflicts: 1, started: '2026-05-20' },
];

export const mockAgents = [
  { id: '1', name: 'ARIA-7', role: 'Coordinator', trust: 0.78, energy: 0.85, risk: 0.2 },
  { id: '2', name: 'NEXUS-3', role: 'Researcher', trust: 0.92, energy: 0.75, risk: 0.15 },
  { id: '3', name: 'ECHO-1', role: 'Analyst', trust: 0.65, energy: 0.6, risk: 0.35 },
];

export const mockConflicts = [
  { id: uuidv4(), severity: 'critical', agents: ['ARIA-7', 'ECHO-1'], type: 'Resource Exhaustion', time: '2m ago' },
  { id: uuidv4(), severity: 'high', agents: ['NEXUS-3', 'ECHO-1'], type: 'Goal Divergence', time: '5m ago' },
];

export const progressData = [
  { tick: 0, agents: 500 },
  { tick: 1, agents: 530 },
  { tick: 2, agents: 560 },
  { tick: 3, agents: 590 },
  { tick: 4, agents: 620 },
];

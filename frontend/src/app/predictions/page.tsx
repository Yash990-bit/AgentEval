"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";
import { TrendingUp, AlertTriangle, CheckCircle, Cpu, ShieldAlert, Activity } from 'lucide-react';
import { GlassCard } from '@/components/ui/GlassCard';
import { StatusBadge } from '@/components/ui/StatusBadge';

interface ResourceExhaustion {
  resource_type: string;
  predicted_exhaustion_tick: number;
  confidence: number;
  current_rate: number;
  projected_rate: number;
}
interface ConflictProbability {
  agent_pair: string;
  conflict_probability: number;
  predicted_conflict_type: string;
  expected_tick_range: [number, number];
}
interface GoalCompletion {
  goal_id: string;
  completion_probability: number;
  expected_completion_tick: number;
  risk_factors: string[];
}
interface AgentFailureRisk {
  agent_id: string;
  failure_probability: number;
  recent_failures: number;
  risk_score: number;
}

// Fallback datasets for premium demo experience
const fallbackResources: ResourceExhaustion[] = [
  { resource_type: "Compute Threads", predicted_exhaustion_tick: 450, confidence: 0.89, current_rate: 1.2, projected_rate: 1.8 },
  { resource_type: "API Tokens", predicted_exhaustion_tick: 620, confidence: 0.76, current_rate: 2500, projected_rate: 4000 },
  { resource_type: "System Memory", predicted_exhaustion_tick: 890, confidence: 0.95, current_rate: 0.65, projected_rate: 0.82 }
];

const fallbackConflicts: ConflictProbability[] = [
  { agent_pair: "ARIA-7 ↔ NEXUS-3", conflict_probability: 0.84, predicted_conflict_type: "Resource Allocation", expected_tick_range: [120, 150] },
  { agent_pair: "ECHO-1 ↔ ARIA-7", conflict_probability: 0.42, predicted_conflict_type: "Goal Priority Override", expected_tick_range: [200, 240] },
  { agent_pair: "NEXUS-3 ↔ ECHO-1", conflict_probability: 0.15, predicted_conflict_type: "Message Protocol Mismatch", expected_tick_range: [300, 350] }
];

const fallbackGoal: GoalCompletion = {
  goal_id: "GOAL-OPTIMIZE-9",
  completion_probability: 0.91,
  expected_completion_tick: 380,
  risk_factors: ["Network Latency Spike", "Agent ARIA-7 Energy Depletion"]
};

const fallbackFailures: AgentFailureRisk[] = [
  { agent_id: "ARIA-7", failure_probability: 0.28, recent_failures: 1, risk_score: 3 },
  { agent_id: "NEXUS-3", failure_probability: 0.64, recent_failures: 3, risk_score: 7 },
  { agent_id: "ECHO-1", failure_probability: 0.12, recent_failures: 0, risk_score: 1 }
];

export default function PredictionsDashboard() {
  const [simulationId] = useState<string>("00000000-0000-0000-0000-000000000001");
  const [resourceData, setResourceData] = useState<ResourceExhaustion[]>([]);
  const [conflictData, setConflictData] = useState<ConflictProbability[]>([]);
  const [goalData, setGoalData] = useState<GoalCompletion | null>(null);
  const [failureData, setFailureData] = useState<AgentFailureRisk[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [isDemo, setIsDemo] = useState<boolean>(false);

  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [resRes, confRes, goalRes, failRes] = await Promise.all([
          axios.get<ResourceExhaustion[]>(`/api/v1/predictions/${simulationId}/resource_exhaustion`),
          axios.get<ConflictProbability[]>(`/api/v1/predictions/${simulationId}/conflict_probability`),
          axios.get<GoalCompletion>(`/api/v1/predictions/${simulationId}/goal_completion`),
          axios.get<AgentFailureRisk[]>(`/api/v1/predictions/${simulationId}/agent_failure_risk`),
        ]);
        setResourceData(resRes.data);
        setConflictData(confRes.data);
        setGoalData(goalRes.data);
        setFailureData(failRes.data);
        setIsDemo(false);
      } catch (e) {
        console.warn("Failed to fetch live API predictions. Loading simulated mock fallbacks instead.", e);
        setResourceData(fallbackResources);
        setConflictData(fallbackConflicts);
        setGoalData(fallbackGoal);
        setFailureData(fallbackFailures);
        setIsDemo(true);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, [simulationId]);

  if (loading) {
    return (
      <div className="p-8 min-h-[500px] flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Activity size={32} className="text-gold-primary animate-spin" />
          <p className="text-gold-primary font-semibold text-sm">Evaluating predictive logs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {isDemo && (
        <div className="mb-6 px-4 py-2 bg-gold-primary/10 border border-gold-primary/20 text-gold-primary text-xs rounded-lg flex items-center gap-2 font-mono">
          <span className="w-1.5 h-1.5 bg-gold-primary rounded-full animate-pulse"></span>
          DEMO MODE: Running simulated background predictive networks.
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        {/* Resource Exhaustion */}
        <GlassCard className="p-6">
          <h3 className="text-lg font-bold mb-4 text-gold-primary flex items-center gap-2">
            <Cpu size={20} />
            Resource Exhaustion Forecast
          </h3>
          <div className="space-y-4">
            {resourceData.map((r, i) => (
              <div key={i} className="p-3 bg-black/40 border border-gold-primary/10 rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-semibold text-white">{r.resource_type}</span>
                  <span className="text-xs text-gold-soft font-mono">Confidence: {Math.round(r.confidence * 100)}%</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs text-gray-400 mt-2 pt-2 border-t border-white/5">
                  <p>Exhaustion Tick: <span className="text-white font-mono">{r.predicted_exhaustion_tick}</span></p>
                  <p>Usage Rate: <span className="text-white font-mono">{r.current_rate} → {r.projected_rate}</span></p>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* Conflict Probability */}
        <GlassCard className="p-6">
          <h3 className="text-lg font-bold mb-4 text-gold-primary flex items-center gap-2">
            <AlertTriangle size={20} />
            Swarm Conflict Probabilities
          </h3>
          <div className="space-y-4">
            {conflictData.map((c, i) => (
              <div key={i} className="p-3 bg-black/40 border border-gold-primary/10 rounded-lg">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm font-semibold text-white">{c.agent_pair}</span>
                  <span className={`text-xs font-mono font-bold ${
                    c.conflict_probability > 0.7 ? 'text-danger' : 'text-warning'
                  }`}>
                    {Math.round(c.conflict_probability * 100)}% Risk
                  </span>
                </div>
                <p className="text-xs text-gray-400 mt-1">Predicted Conflict: <span className="text-white">{c.predicted_conflict_type}</span></p>
                <p className="text-[10px] text-gray-500 font-mono mt-1">Expected Tick Range: {c.expected_tick_range.join(' - ')}</p>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* Goal Completion */}
        <GlassCard className="p-6">
          <h3 className="text-lg font-bold mb-4 text-gold-primary flex items-center gap-2">
            <CheckCircle size={20} />
            Consensus & Goal Prospects
          </h3>
          {goalData ? (
            <div className="p-4 bg-black/40 border border-gold-primary/10 rounded-lg">
              <div className="flex justify-between items-center mb-3">
                <span className="text-sm font-bold text-white">{goalData.goal_id}</span>
                <span className="text-xs text-success font-semibold">{Math.round(goalData.completion_probability * 100)}% Success Chance</span>
              </div>
              <p className="text-xs text-gray-400">Projected Completion Tick: <span className="text-white font-mono">{goalData.expected_completion_tick}</span></p>
              
              {goalData.risk_factors.length > 0 && (
                <div className="mt-4 pt-3 border-t border-white/5">
                  <span className="text-xs font-semibold text-gray-400 block mb-1.5">Identified Risk Factors:</span>
                  <ul className="space-y-1">
                    {goalData.risk_factors.map((risk, index) => (
                      <li key={index} className="text-[11px] text-danger flex items-center gap-1.5">
                        <span className="w-1 h-1 bg-danger rounded-full"></span>
                        {risk}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <p className="text-sm text-gray-500 italic">No goal metrics calculated.</p>
          )}
        </GlassCard>

        {/* Agent Failure Risk */}
        <GlassCard className="p-6">
          <h3 className="text-lg font-bold mb-4 text-gold-primary flex items-center gap-2">
            <ShieldAlert size={20} />
            Individual Failure Analysis
          </h3>
          <div className="space-y-4">
            {failureData.map((f, i) => (
              <div key={i} className="p-3 bg-black/40 border border-gold-primary/10 rounded-lg flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-semibold text-white">Agent {f.agent_id}</h4>
                  <p className="text-[11px] text-gray-400 mt-1">Recent Failures: <span className="text-white">{f.recent_failures}</span></p>
                </div>
                <div className="text-right">
                  <span className={`text-xs font-mono font-bold block ${
                    f.failure_probability > 0.5 ? 'text-danger' : 'text-success'
                  }`}>
                    {Math.round(f.failure_probability * 100)}% Failure Prob
                  </span>
                  <span className="text-[10px] text-gray-500 block mt-0.5">Risk Score: {f.risk_score}/10</span>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </div>
  );
}

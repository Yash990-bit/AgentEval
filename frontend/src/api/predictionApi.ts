// frontend/src/api/predictionApi.ts
import axios from 'axios';

const API_BASE = '/api/v1/predictions';

export interface ResourceExhaustion {
  resource_type: string;
  predicted_exhaustion_tick: number;
  confidence: number;
  current_rate: number;
  projected_rate: number;
}

export interface ConflictProbability {
  agent_pair: string;
  conflict_probability: number;
  predicted_conflict_type: string;
  expected_tick_range: [number, number];
}

export interface GoalCompletion {
  goal_id: string;
  completion_probability: number;
  expected_completion_tick: number;
  risk_factors: string[];
}

export interface AgentFailureRisk {
  agent_id: string;
  failure_probability: number;
  recent_failures: number;
  risk_score: number;
}

export const getResourceExhaustion = async (simId: string): Promise<ResourceExhaustion[]> => {
  const res = await axios.get<ResourceExhaustion[]>(`${API_BASE}/${simId}/resource_exhaustion`);
  return res.data;
};

export const getConflictProbability = async (simId: string): Promise<ConflictProbability[]> => {
  const res = await axios.get<ConflictProbability[]>(`${API_BASE}/${simId}/conflict_probability`);
  return res.data;
};

export const getGoalCompletion = async (simId: string): Promise<GoalCompletion> => {
  const res = await axios.get<GoalCompletion>(`${API_BASE}/${simId}/goal_completion`);
  return res.data;
};

export const getAgentFailureRisk = async (simId: string): Promise<AgentFailureRisk[]> => {
  const res = await axios.get<AgentFailureRisk[]>(`${API_BASE}/${simId}/agent_failure_risk`);
  return res.data;
};

// Types for the Agent Marketplace UI
export interface Template {
  id: string;
  name: string;
  role: RoleEnum;
  description: string;
  system_prompt: string;
  created_at?: string;
  use_count?: number;
  avg_performance_score?: number;
}

export type RoleEnum =
  | "research"
  | "coding"
  | "data_analyst"
  | "customer_support"
  | "strategic_planner"
  | "security_auditor"
  | "negotiator"
  | "coordinator";

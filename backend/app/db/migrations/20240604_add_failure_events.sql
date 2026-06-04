-- Migration: add failure_events table
CREATE TABLE IF NOT EXISTS failure_events (
    id SERIAL PRIMARY KEY,
    simulation_id VARCHAR(36) NOT NULL,
    agent_id VARCHAR(100) NOT NULL,
    failure_type VARCHAR(100) NOT NULL,
    tick_occurred INTEGER NOT NULL,
    severity VARCHAR(50) NOT NULL,
    propagated_to JSONB DEFAULT '[]'::jsonb,
    recovery_action TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at_tick INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_failure_simulation ON failure_events (simulation_id);
CREATE INDEX IF NOT EXISTS idx_failure_agent ON failure_events (agent_id);

-- Migration: add shared_memory_pools and episodic_memories tables
CREATE TABLE IF NOT EXISTS shared_memory_pools (
    id SERIAL PRIMARY KEY,
    simulation_id INTEGER NOT NULL,
    agent_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    tags JSONB DEFAULT '[]'::jsonb,
    version INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_shared_simulation_agent ON shared_memory_pools (simulation_id, agent_id);

CREATE TABLE IF NOT EXISTS episodic_memories (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER NOT NULL,
    simulation_id INTEGER NOT NULL,
    tick INTEGER NOT NULL,
    episode_type TEXT NOT NULL,
    context_snapshot JSONB NOT NULL,
    outcome TEXT,
    emotional_valence FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_episodic_agent_simulation ON episodic_memories (agent_id, simulation_id);

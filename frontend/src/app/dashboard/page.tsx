"use client"

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
// Added FailureDashboard import and rendering
import Link from "next/link";
import FailureDashboard from '@/components/FailureDashboard';

// Inside the CardContent, after ConflictDashboard and before EmergentDashboard, add FailureDashboard component
// (We'll modify the JSX accordingly in subsequent edit)
import ConflictDashboard from '@/components/ConflictDashboard';
import EmergentDashboard from '@/components/EmergentDashboard';

export default function Dashboard() {
  const [running, setRunning] = useState(false);
  const [agents, setAgents] = useState<any[]>([]);
  const [links, setLinks] = useState<any[]>([]);
  const [simulationId, setSimulationId] = useState('default');

  const fetchInitialAgents = async () => {
    try {
      const res = await axios.get('/api/v1/agents');
      setAgents(res.data);
    } catch (err) {
      console.error("Failed to load agents on dashboard", err);
    }
  };

  useEffect(() => {
    fetchInitialAgents();
  }, []);

  useEffect(() => {
    if (!running) return;
    const interval = setInterval(async () => {
      try {
        const res = await axios.post('/api/v1/simulation/step');
        if (res.data) {
          if (res.data.agents) {
            setAgents(res.data.agents);
          }
          if (res.data.links) {
            setLinks(res.data.links);
          }
        }
      } catch (err) {
        console.error("Error stepping simulation", err);
      }
    }, 1500);
    return () => clearInterval(interval);
  }, [running]);

  const handleStart = async () => {
    try {
      // Map the active agents correctly to backend model expectations
      const agentsPayload = agents.map((a: any) => ({
        id: a.id || `agent-${Math.random()}`,
        name: a.name,
        role: a.role,
        objective: a.objective || a.description || "Simulated objective",
        trust_score: a.trust_score !== undefined ? a.trust_score : (a.trust !== undefined ? a.trust : 0.8),
        energy_score: a.energy_score !== undefined ? a.energy_score : (a.energy !== undefined ? a.energy * 100 : 100.0),
        risk_score: a.risk_score !== undefined ? a.risk_score : (a.risk !== undefined ? a.risk : 0.1),
      }));
      await axios.post('/api/v1/simulation/start', { agents: agentsPayload });
    } catch (e) {
      console.error("Error starting simulation", e);
    }
    setRunning(true);
  };

  const handlePause = async () => {
    try {
      await axios.post('/api/v1/simulation/stop');
    } catch (e) {
      console.error("Error pausing simulation", e);
    }
    setRunning(false);
  };

  const handleReset = () => {
    setRunning(false);
    setLinks([]);
    fetchInitialAgents();
  };

  return (
    <Card className="glass mx-auto mt-12 max-w-4xl overflow-hidden shadow-xl">
      <CardHeader className="bg-primary/20 p-4">
        <CardTitle className="text-primary-foreground">AI Agent Behaviour Simulator</CardTitle>
      </CardHeader>
      <CardContent className="p-4">
        <div className="flex justify-center gap-4 mb-4">
          <Button onClick={handleStart} disabled={running}>Start</Button>
          <Button variant="secondary" onClick={handlePause} disabled={!running}>Pause</Button>
          <Button variant="destructive" onClick={handleReset}>Reset</Button>
          <Link href="/predictions" className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors">Predictions</Link>
        </div>
        <ConflictDashboard agents={agents} links={links} />
        <FailureDashboard simulationId={simulationId} />
        <EmergentDashboard simulationId={simulationId} />
      </CardContent>
    </Card>
  );
}

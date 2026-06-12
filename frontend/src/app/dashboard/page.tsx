"use client"

import React, { useState } from 'react';
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
  const [agents, setAgents] = useState([]);
  const [links, setLinks] = useState([]);
  const [simulationId, setSimulationId] = useState('default');

  const handleStart = async () => {
    try {
      await axios.post('/api/v1/simulation/start');
    } catch (e) {
      console.error(e);
    }
    setRunning(true);
  };

  const handlePause = async () => {
    try {
      await axios.post('/api/v1/simulation/stop');
    } catch (e) {
      console.error(e);
    }
    setRunning(false);
  };


  const handleReset = () => {
    setRunning(false);
    setAgents([]);
    setLinks([]);
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

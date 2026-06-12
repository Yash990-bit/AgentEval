"use client";
import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip as ReTooltip,
  ResponsiveContainer,
} from 'recharts';
import { GlassCard } from '@/components/ui/GlassCard';

export default function AnalyticsPage() {
  const usageData = [
    { day: 'Mon', tokens: 150 },
    { day: 'Tue', tokens: 200 },
    { day: 'Wed', tokens: 180 },
    { day: 'Thu', tokens: 220 },
    { day: 'Fri', tokens: 260 },
    { day: 'Sat', tokens: 300 },
    { day: 'Sun', tokens: 280 },
  ];

  const successData = [
    { role: 'Coordinator', completed: 92, failed: 8 },
    { role: 'Researcher', completed: 85, failed: 15 },
    { role: 'Analyst', completed: 74, failed: 26 },
  ];

  return (
    <div className="p-8">
      <GlassCard className="p-8">
        <h3 className="text-2xl font-bold mb-6 text-gold-primary">Analytics</h3>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="h-80">
            <h4 className="mb-4 text-gold-primary font-semibold">Weekly Token Usage</h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={usageData}>
                <XAxis dataKey="day" stroke="var(--gold-primary)" />
                <YAxis stroke="var(--gold-primary)" />
                <ReTooltip contentStyle={{ backgroundColor: 'rgba(26,26,26,0.9)', border: 'none', color: '#fff' }} />
                <Bar dataKey="tokens" fill="var(--gold-primary)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="h-80">
            <h4 className="mb-4 text-gold-primary font-semibold">Goal Completion by Role</h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={successData}>
                <XAxis dataKey="role" stroke="var(--gold-primary)" />
                <YAxis stroke="var(--gold-primary)" />
                <ReTooltip contentStyle={{ backgroundColor: 'rgba(26,26,26,0.9)', border: 'none', color: '#fff' }} />
                <Bar dataKey="completed" fill="var(--gold-primary)" />
                <Bar dataKey="failed" fill="var(--danger)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </GlassCard>
    </div>
  );
}

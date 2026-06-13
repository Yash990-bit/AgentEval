"use client";
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bot, CheckCircle2, AlertOctagon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { GlassCard } from '@/components/ui/GlassCard';
import { GoldButton } from '@/components/ui/GoldButton';

export default function AgentManagementPage() {
  const [agents, setAgents] = useState<any[]>([]);
  const [notification, setNotification] = useState<string | null>(null);

  const fetchAgents = async () => {
    try {
      const res = await axios.get('/api/v1/agents');
      setAgents(res.data.map((a: any) => ({
        id: a.id,
        name: a.name,
        role: a.role,
        description: a.description || a.objective,
        status: a.status,
        trust: a.trust_score,
        energy: a.energy_score,
        risk: a.risk_score,
        goalsCompleted: a.goals_completed,
        messagesSent: a.messages_sent,
        conflictsInvolved: a.conflicts_involved,
        tokensUsed: a.tokens_used,
        active: a.status !== 'failed'
      })));
    } catch (err) {
      console.error("Failed to load agents in management view", err);
    }
  };

  useEffect(() => {
    fetchAgents();
  }, []);

  const toggleAgent = (id: string, name: string, active: boolean) => {
    setAgents(prev =>
      prev.map(a => (a.id === id ? { ...a, active: !a.active } : a))
    );
    setNotification(`${name} is now ${active ? 'inactive' : 'active'}`);
    setTimeout(() => setNotification(null), 3000);
  };

  return (
    <div className="p-8 relative">
      {/* Toast Notification */}
      <AnimatePresence>
        {notification && (
          <motion.div
            initial={{ opacity: 0, y: -20, x: 20 }}
            animate={{ opacity: 1, y: 0, x: 0 }}
            exit={{ opacity: 0, y: -20, x: 20 }}
            className="fixed top-20 right-8 z-50 flex items-center gap-3 px-4 py-3 bg-black/90 border border-gold-primary/30 rounded-lg shadow-[0_0_15px_rgba(212,175,55,0.25)] backdrop-blur-md"
          >
            <CheckCircle2 size={18} className="text-gold-primary animate-pulse" />
            <span className="text-sm font-semibold text-white">{notification}</span>
          </motion.div>
        )}
      </AnimatePresence>

      <GlassCard className="p-8">
        <h3 className="text-2xl font-bold mb-6 text-gold-primary">Agent Management</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map((a) => (
            <GlassCard
              key={a.id}
              className={`p-6 flex flex-col items-center transition-all duration-300 relative overflow-hidden ${
                !a.active ? 'opacity-40 grayscale scale-95 border-dashed border-gray-600' : ''
              }`}
            >
              <Bot size={40} className={`${a.active ? 'text-gold-primary animate-pulse' : 'text-gray-500'} mb-3`} />
              
              {!a.active && (
                <div className="absolute top-2 right-2 bg-red-950/40 border border-red-500/30 text-danger px-2 py-0.5 rounded text-[10px] flex items-center gap-1 font-semibold uppercase">
                  <AlertOctagon size={12} />
                  Offline
                </div>
              )}
              
              <h4 className="text-xl font-semibold text-white mb-1">{a.name}</h4>
              <p className="text-sm text-gray-300 font-medium mb-4">Role: {a.role}</p>
              
              <div className="w-full space-y-3">
                <div>
                  <div className="flex justify-between text-xs text-gray-400 font-medium mb-1">
                    <span>Trust Factor</span>
                    <span className="text-success">{Math.round(a.trust * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-800 rounded-full h-1.5 overflow-hidden">
                    <div className="h-full bg-success rounded-full transition-all duration-500" style={{ width: `${a.trust * 100}%` }} />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-xs text-gray-400 font-medium mb-1">
                    <span>Energy Resource</span>
                    <span className="text-info">{Math.round(a.energy * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-800 rounded-full h-1.5 overflow-hidden">
                    <div className="h-full bg-info rounded-full transition-all duration-500" style={{ width: `${a.energy * 100}%` }} />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-xs text-gray-400 font-medium mb-1">
                    <span>Risk Level</span>
                    <span className="text-danger">{Math.round(a.risk * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-800 rounded-full h-1.5 overflow-hidden">
                    <div className="h-full bg-danger rounded-full transition-all duration-500" style={{ width: `${a.risk * 100}%` }} />
                  </div>
                </div>
              </div>

              <div className="mt-6 flex gap-3 w-full">
                <GoldButton variant="outline" className="flex-1 py-1.5 text-xs">
                  Edit Profile
                </GoldButton>
                <GoldButton
                  variant="outline"
                  className={`flex-1 py-1.5 text-xs ${a.active ? 'hover:border-danger hover:text-danger' : 'hover:border-success hover:text-success'}`}
                  onClick={() => toggleAgent(a.id, a.name, a.active)}
                >
                  {a.active ? 'Deactivate' : 'Activate'}
                </GoldButton>
              </div>
            </GlassCard>
          ))}
        </div>
      </GlassCard>
    </div>
  );
}

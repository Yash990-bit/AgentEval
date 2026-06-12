"use client";
import React, { useState } from 'react';
import { Eye, EyeOff, Save, ShieldAlert, Sparkles, Bell } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { GlassCard } from '@/components/ui/GlassCard';
import { GoldButton } from '@/components/ui/GoldButton';

export default function SettingsPage() {
  const [theme, setTheme] = useState('dark');
  const [geminiKey, setGeminiKey] = useState('••••••••••••••••••••••••••••••••');
  const [openaiKey, setOpenaiKey] = useState('••••••••••••••••••••••••••••••••');
  const [showGemini, setShowGemini] = useState(false);
  const [showOpenai, setShowOpenai] = useState(false);
  
  const [notifyConflicts, setNotifyConflicts] = useState(true);
  const [notifyResource, setNotifyResource] = useState(true);
  const [notifyConsensus, setNotifyConsensus] = useState(false);

  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaving(true);
    setTimeout(() => {
      setSaving(false);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    }, 1500);
  };

  return (
    <div className="p-8 relative">
      <AnimatePresence>
        {saved && (
          <motion.div
            initial={{ opacity: 0, y: -20, x: 20 }}
            animate={{ opacity: 1, y: 0, x: 0 }}
            exit={{ opacity: 0, y: -20, x: 20 }}
            className="fixed top-20 right-8 z-50 flex items-center gap-3 px-4 py-3 bg-black/90 border border-gold-primary/30 rounded-lg shadow-[0_0_15px_rgba(212,175,55,0.25)] backdrop-blur-md"
          >
            <Sparkles size={18} className="text-gold-primary animate-spin-slow" />
            <span className="text-sm font-semibold text-white">Configuration saved successfully!</span>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Core Settings */}
        <div className="md:col-span-2 space-y-6">
          <GlassCard className="p-6">
            <h3 className="text-xl font-bold mb-6 text-gold-primary flex items-center gap-2">
              <Sparkles size={20} />
              Model Provider Integration
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Gemini API Key</label>
                <div className="relative flex rounded-md bg-black/50 border border-gold-primary/20 overflow-hidden">
                  <input
                    type={showGemini ? 'text' : 'password'}
                    value={geminiKey}
                    onChange={(e) => setGeminiKey(e.target.value)}
                    className="flex-1 bg-transparent px-3 py-2 text-sm text-white focus:outline-none"
                  />
                  <button
                    onClick={() => setShowGemini(!showGemini)}
                    className="px-3 hover:bg-gold-primary/10 text-gray-400 hover:text-white transition-colors"
                  >
                    {showGemini ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">OpenAI API Key</label>
                <div className="relative flex rounded-md bg-black/50 border border-gold-primary/20 overflow-hidden">
                  <input
                    type={showOpenai ? 'text' : 'password'}
                    value={openaiKey}
                    onChange={(e) => setOpenaiKey(e.target.value)}
                    className="flex-1 bg-transparent px-3 py-2 text-sm text-white focus:outline-none"
                  />
                  <button
                    onClick={() => setShowOpenai(!showOpenai)}
                    className="px-3 hover:bg-gold-primary/10 text-gray-400 hover:text-white transition-colors"
                  >
                    {showOpenai ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>
            </div>
          </GlassCard>

          <GlassCard className="p-6">
            <h3 className="text-xl font-bold mb-6 text-gold-primary flex items-center gap-2">
              <Bell size={20} />
              Event Notifications
            </h3>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-2 border-b border-gold-primary/5">
                <div>
                  <h4 className="text-sm font-semibold text-white">Conflict Detections</h4>
                  <p className="text-xs text-gray-400 mt-0.5">Push notices when agents hit priority deadlocks.</p>
                </div>
                <input
                  type="checkbox"
                  checked={notifyConflicts}
                  onChange={(e) => setNotifyConflicts(e.target.checked)}
                  className="w-4 h-4 cursor-pointer accent-gold-primary"
                />
              </div>

              <div className="flex items-center justify-between p-2 border-b border-gold-primary/5">
                <div>
                  <h4 className="text-sm font-semibold text-white">Resource Warnings</h4>
                  <p className="text-xs text-gray-400 mt-0.5">Alerts when token limits or budgets exceed 80% capacity.</p>
                </div>
                <input
                  type="checkbox"
                  checked={notifyResource}
                  onChange={(e) => setNotifyResource(e.target.checked)}
                  className="w-4 h-4 cursor-pointer accent-gold-primary"
                />
              </div>

              <div className="flex items-center justify-between p-2">
                <div>
                  <h4 className="text-sm font-semibold text-white">Consensus Updates</h4>
                  <p className="text-xs text-gray-400 mt-0.5">Ping when swarm-wide goal agreements are reached.</p>
                </div>
                <input
                  type="checkbox"
                  checked={notifyConsensus}
                  onChange={(e) => setNotifyConsensus(e.target.checked)}
                  className="w-4 h-4 cursor-pointer accent-gold-primary"
                />
              </div>
            </div>
          </GlassCard>
        </div>

        {/* Display Settings & Actions */}
        <div className="space-y-6">
          <GlassCard className="p-6">
            <h3 className="text-xl font-bold mb-6 text-gold-primary flex items-center gap-2">
              <ShieldAlert size={20} />
              Visual Interface
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Theme Profile</label>
                <select
                  value={theme}
                  onChange={(e) => setTheme(e.target.value)}
                  className="w-full bg-black/50 border border-gold-primary/20 rounded px-3 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-gold-primary"
                >
                  <option value="dark" className="bg-gray-900 text-white">Gold Cyberpunk (Dark)</option>
                  <option value="light" className="bg-gray-900 text-white">Golden Hour (Light)</option>
                  <option value="system" className="bg-gray-900 text-white">OS System Sync</option>
                </select>
              </div>

              <div className="pt-2">
                <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider block mb-1">Local Node State</span>
                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 bg-gold-primary/10 text-gold-primary border border-gold-primary/20 rounded text-[10px] font-mono">
                  NODE VERSION: v22.0.0
                </span>
              </div>
            </div>
          </GlassCard>

          <GlassCard className="p-6 flex flex-col gap-4 items-stretch justify-center text-center">
            <p className="text-xs text-gray-400 leading-relaxed">Ensure all provider API keys are correctly active before launching new autonomous agent simulations.</p>
            <GoldButton variant="primary" onClick={handleSave} disabled={saving} className="flex items-center justify-center gap-2 py-2.5">
              <Save size={16} />
              {saving ? 'Saving...' : 'Save Configuration'}
            </GoldButton>
          </GlassCard>
        </div>
      </div>
    </div>
  );
}

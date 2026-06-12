"use client";
import React from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Monitor, Shield, Cpu, RefreshCw, Layers } from 'lucide-react';
import { GlassCard } from '@/components/ui/GlassCard';
import { GoldButton } from '@/components/ui/GoldButton';
import { StatusBadge } from '@/components/ui/StatusBadge';

export default function ScreenDetailClient({ slug }: { slug: string }) {
  const router = useRouter();

  // Format the slug to a title
  const title = slug
    ? slug
        .split('-')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ')
    : 'System Template';

  return (
    <div className="p-8">
      <div className="mb-6 flex items-center justify-between">
        <GoldButton variant="outline" className="flex items-center gap-2" onClick={() => router.push('/screens')}>
          <ArrowLeft size={16} />
          Back to Templates
        </GoldButton>
        <StatusBadge status="running" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Screen Details Panel */}
        <div className="space-y-6">
          <GlassCard className="p-6">
            <h3 className="text-xl font-bold text-gold-primary mb-2 flex items-center gap-2">
              <Monitor size={20} />
              {title}
            </h3>
            <p className="text-xs font-mono text-gray-500 mb-4">SLUG: {slug}</p>
            <p className="text-sm text-gray-300 mb-4 leading-relaxed">
              This preset interface frame represents a high-fidelity dashboard layout designed for agent communication and consensus tracking.
            </p>

            <div className="border-t border-gold-primary/10 pt-4 space-y-3">
              <div className="flex justify-between text-xs">
                <span className="text-gray-400">Target Device</span>
                <span className="text-white font-semibold">Desktop (1920x1080)</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-400">Layout Class</span>
                <span className="text-white font-mono">grid-cols-12 gap-6</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-400">Consensus Engine</span>
                <span className="text-gold-soft">Active</span>
              </div>
            </div>
          </GlassCard>

          <GlassCard className="p-6">
            <h4 className="text-sm font-bold text-gold-primary mb-3 flex items-center gap-2">
              <Cpu size={16} />
              Telemetry Schema
            </h4>
            <pre className="text-[10px] bg-black/60 p-3 rounded border border-gold-primary/10 text-gold-soft overflow-x-auto font-mono">
{`{
  "screen": "${slug}",
  "status": "synchronized",
  "components": [
    "KPI_Grid",
    "Flow_Graph",
    "Consensus_Timeline"
  ],
  "refreshRate": "1000ms"
}`}
            </pre>
          </GlassCard>
        </div>

        {/* Mock Screen Preview Frame */}
        <div className="lg:col-span-2">
          <GlassCard className="p-4 flex flex-col h-[520px] relative overflow-hidden group">
            {/* Monitor Chrome */}
            <div className="flex items-center justify-between px-3 py-2 bg-black/80 border-b border-gold-primary/10 rounded-t-lg">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-danger/80"></span>
                <span className="w-2.5 h-2.5 rounded-full bg-warning/80"></span>
                <span className="w-2.5 h-2.5 rounded-full bg-success/80"></span>
              </div>
              <span className="text-[10px] font-mono text-gray-500">Preview: {title}</span>
              <RefreshCw size={10} className="text-gray-500 animate-spin-slow" />
            </div>

            {/* Mock Screen Canvas */}
            <div className="flex-1 bg-[#050505] p-6 relative flex flex-col justify-between overflow-y-auto">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h2 className="text-lg font-bold text-white tracking-wide">{title}</h2>
                  <p className="text-xs text-gray-400">Sub-system Operations Console</p>
                </div>
                <div className="flex gap-2">
                  <span className="w-8 h-8 rounded bg-gold-primary/10 border border-gold-primary/20 flex items-center justify-center text-gold-primary text-xs font-mono font-bold">A7</span>
                  <span className="w-8 h-8 rounded bg-gold-primary/10 border border-gold-primary/20 flex items-center justify-center text-gold-primary text-xs font-mono font-bold">N3</span>
                </div>
              </div>

              {/* Layout Blocks */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="p-4 bg-black/40 border border-gold-primary/10 rounded flex flex-col gap-1">
                    <span className="text-[10px] text-gray-500 font-mono">PARAMETER_0{i}</span>
                    <span className="text-xl font-bold text-gold-primary font-mono">{i * 24.5}%</span>
                  </div>
                ))}
              </div>

              {/* Wireframe graph placeholder */}
              <div className="flex-1 border border-dashed border-gold-primary/20 rounded-lg flex flex-col items-center justify-center p-6 bg-gold-primary/5 min-h-[160px] mb-6">
                <Shield size={32} className="text-gold-primary mb-2 opacity-40 animate-pulse" />
                <p className="text-xs font-semibold text-gray-300">Mock Data Visualization Stream</p>
                <p className="text-[10px] text-gray-500 mt-1 text-center font-mono">Consensus vector nodes resolved successfully.</p>
              </div>

              {/* Footer status bar */}
              <div className="flex justify-between items-center text-[10px] text-gray-500 font-mono border-t border-gold-primary/10 pt-4">
                <span className="flex items-center gap-1"><Layers size={10} className="text-gold-primary" /> SYSTEM_ONLINE</span>
                <span>SECURE SSL 256-BIT</span>
              </div>
            </div>
          </GlassCard>
        </div>
      </div>
    </div>
  );
}

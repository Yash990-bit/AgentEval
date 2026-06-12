import React from 'react';
import TrustGraph from '@/components/TrustGraph';
import { GlassCard } from '@/components/ui/GlassCard';
import { Shield } from 'lucide-react';

const simulationId = 'demo-simulation';

export default function TrustPage() {
  return (
    <div className="p-8">
      <GlassCard className="p-8">
        <h3 className="text-2xl font-bold mb-6 text-gold-primary flex items-center gap-2">
          <Shield size={24} />
          Agent Trust Matrix Network
        </h3>
        <p className="text-sm text-gray-400 mb-6">
          Real-time dynamic visualization of directional trust relationships, communication pathways, and affinity scores between agent processes.
        </p>
        <TrustGraph simulationId={simulationId} />
      </GlassCard>
    </div>
  );
}

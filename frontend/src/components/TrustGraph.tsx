"use client";
import React, { useState } from 'react';
import { Bot, Info, ShieldAlert, Award } from 'lucide-react';
import { GlassCard } from './ui/GlassCard';

interface TrustGraphProps {
  simulationId: string;
}

export const TrustGraph: React.FC<TrustGraphProps> = ({ simulationId }) => {
  // State for directional trust scores
  const [ariaToNexus, setAriaToNexus] = useState(0.92);
  const [nexusToAria, setNexusToAria] = useState(0.88);
  const [nexusToEcho, setNexusToEcho] = useState(0.75);
  const [echoToNexus, setEchoToNexus] = useState(0.61);
  const [echoToAria, setEchoToAria] = useState(0.45);
  const [ariaToEcho, setAriaToEcho] = useState(0.58);

  const [hoveredEdge, setHoveredEdge] = useState<string | null>(null);

  // Helper to resolve edge colors
  const getTrustColor = (val: number) => {
    if (val >= 0.8) return '#00C896'; // Green
    if (val >= 0.6) return '#D4AF37'; // Gold
    return '#FF4444'; // Red
  };

  return (
    <div className="grid md:grid-cols-3 gap-6">
      {/* SVG Canvas Map */}
      <div className="md:col-span-2 relative flex items-center justify-center p-4 bg-black/50 border border-gold-primary/10 rounded-xl min-h-[420px]">
        <svg viewBox="0 0 600 400" className="w-full h-full max-w-[500px]">
          <defs>
            {/* Arrow markers for directional lines */}
            <marker id="arrow-green" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#00C896" />
            </marker>
            <marker id="arrow-gold" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#D4AF37" />
            </marker>
            <marker id="arrow-red" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#FF4444" />
            </marker>
          </defs>

          {/* Connection Lines (Paths) */}
          
          {/* ARIA-7 (300, 80) <-> NEXUS-3 (480, 280) */}
          {/* Aria -> Nexus */}
          <path
            d="M 300 80 Q 420 150 480 280"
            fill="none"
            stroke={getTrustColor(ariaToNexus)}
            strokeWidth={1 + ariaToNexus * 4}
            markerEnd={`url(#arrow-${ariaToNexus >= 0.8 ? 'green' : ariaToNexus >= 0.6 ? 'gold' : 'red'})`}
            className="cursor-pointer transition-all duration-300 hover:stroke-white"
            onMouseEnter={() => setHoveredEdge(`ARIA-7 ➔ NEXUS-3: ${Math.round(ariaToNexus * 100)}%`)}
            onMouseLeave={() => setHoveredEdge(null)}
          />
          {/* Nexus -> Aria */}
          <path
            d="M 480 280 Q 360 210 300 80"
            fill="none"
            stroke={getTrustColor(nexusToAria)}
            strokeWidth={1 + nexusToAria * 4}
            markerEnd={`url(#arrow-${nexusToAria >= 0.8 ? 'green' : nexusToAria >= 0.6 ? 'gold' : 'red'})`}
            className="cursor-pointer transition-all duration-300 hover:stroke-white"
            onMouseEnter={() => setHoveredEdge(`NEXUS-3 ➔ ARIA-7: ${Math.round(nexusToAria * 100)}%`)}
            onMouseLeave={() => setHoveredEdge(null)}
          />

          {/* NEXUS-3 (480, 280) <-> ECHO-1 (120, 280) */}
          {/* Nexus -> Echo */}
          <path
            d="M 480 280 Q 300 310 120 280"
            fill="none"
            stroke={getTrustColor(nexusToEcho)}
            strokeWidth={1 + nexusToEcho * 4}
            markerEnd={`url(#arrow-${nexusToEcho >= 0.8 ? 'green' : nexusToEcho >= 0.6 ? 'gold' : 'red'})`}
            className="cursor-pointer transition-all duration-300 hover:stroke-white"
            onMouseEnter={() => setHoveredEdge(`NEXUS-3 ➔ ECHO-1: ${Math.round(nexusToEcho * 100)}%`)}
            onMouseLeave={() => setHoveredEdge(null)}
          />
          {/* Echo -> Nexus */}
          <path
            d="M 120 280 Q 300 250 480 280"
            fill="none"
            stroke={getTrustColor(echoToNexus)}
            strokeWidth={1 + echoToNexus * 4}
            markerEnd={`url(#arrow-${echoToNexus >= 0.8 ? 'green' : echoToNexus >= 0.6 ? 'gold' : 'red'})`}
            className="cursor-pointer transition-all duration-300 hover:stroke-white"
            onMouseEnter={() => setHoveredEdge(`ECHO-1 ➔ NEXUS-3: ${Math.round(echoToNexus * 100)}%`)}
            onMouseLeave={() => setHoveredEdge(null)}
          />

          {/* ECHO-1 (120, 280) <-> ARIA-7 (300, 80) */}
          {/* Echo -> Aria */}
          <path
            d="M 120 280 Q 180 150 300 80"
            fill="none"
            stroke={getTrustColor(echoToAria)}
            strokeWidth={1 + echoToAria * 4}
            markerEnd={`url(#arrow-${echoToAria >= 0.8 ? 'green' : echoToAria >= 0.6 ? 'gold' : 'red'})`}
            className="cursor-pointer transition-all duration-300 hover:stroke-white"
            onMouseEnter={() => setHoveredEdge(`ECHO-1 ➔ ARIA-7: ${Math.round(echoToAria * 100)}%`)}
            onMouseLeave={() => setHoveredEdge(null)}
          />
          {/* Aria -> Echo */}
          <path
            d="M 300 80 Q 240 210 120 280"
            fill="none"
            stroke={getTrustColor(ariaToEcho)}
            strokeWidth={1 + ariaToEcho * 4}
            markerEnd={`url(#arrow-${ariaToEcho >= 0.8 ? 'green' : ariaToEcho >= 0.6 ? 'gold' : 'red'})`}
            className="cursor-pointer transition-all duration-300 hover:stroke-white"
            onMouseEnter={() => setHoveredEdge(`ARIA-7 ➔ ECHO-1: ${Math.round(ariaToEcho * 100)}%`)}
            onMouseLeave={() => setHoveredEdge(null)}
          />

          {/* Node Circles */}
          {/* ARIA-7 */}
          <g transform="translate(300, 80)" className="cursor-pointer">
            <circle r="28" fill="#1A1A1A" stroke="var(--gold-primary)" strokeWidth="2" />
            <text y="5" textAnchor="middle" fill="#FFF" fontSize="10" fontWeight="bold" fontFamily="monospace">ARIA-7</text>
          </g>

          {/* NEXUS-3 */}
          <g transform="translate(480, 280)" className="cursor-pointer">
            <circle r="28" fill="#1A1A1A" stroke="var(--gold-primary)" strokeWidth="2" />
            <text y="5" textAnchor="middle" fill="#FFF" fontSize="10" fontWeight="bold" fontFamily="monospace">NEXUS-3</text>
          </g>

          {/* ECHO-1 */}
          <g transform="translate(120, 280)" className="cursor-pointer">
            <circle r="28" fill="#1A1A1A" stroke="var(--gold-primary)" strokeWidth="2" />
            <text y="5" textAnchor="middle" fill="#FFF" fontSize="10" fontWeight="bold" fontFamily="monospace">ECHO-1</text>
          </g>
        </svg>

        {/* Hover info tooltip */}
        <div className="absolute bottom-4 left-4 bg-black/90 border border-gold-primary/30 rounded p-2 text-xs font-mono min-w-[150px]">
          <p className="text-gold-primary flex items-center gap-1.5 mb-1">
            <Info size={12} />
            Path Affinity
          </p>
          <p className="text-white">{hoveredEdge || 'Hover on paths'}</p>
        </div>
      </div>

      {/* Adjusters Panel */}
      <GlassCard className="p-5 flex flex-col justify-between">
        <div>
          <h4 className="text-md font-bold text-gold-primary mb-4 flex items-center gap-2">
            <Award size={16} />
            Trust Tuner
          </h4>
          <p className="text-xs text-gray-400 mb-4 leading-relaxed">Manually adjust directional parameters to simulate agent state decay or trust reinforcement.</p>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-300 font-mono">ARIA-7 ➔ NEXUS-3</span>
                <span className="text-gold-soft font-mono">{(ariaToNexus * 100).toFixed(0)}%</span>
              </div>
              <input type="range" min="0" max="1" step="0.01" value={ariaToNexus} onChange={e => setAriaToNexus(parseFloat(e.target.value))} className="w-full accent-gold-primary cursor-pointer" />
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-300 font-mono">NEXUS-3 ➔ ARIA-7</span>
                <span className="text-gold-soft font-mono">{(nexusToAria * 100).toFixed(0)}%</span>
              </div>
              <input type="range" min="0" max="1" step="0.01" value={nexusToAria} onChange={e => setNexusToAria(parseFloat(e.target.value))} className="w-full accent-gold-primary cursor-pointer" />
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-300 font-mono">NEXUS-3 ➔ ECHO-1</span>
                <span className="text-gold-soft font-mono">{(nexusToEcho * 100).toFixed(0)}%</span>
              </div>
              <input type="range" min="0" max="1" step="0.01" value={nexusToEcho} onChange={e => setNexusToEcho(parseFloat(e.target.value))} className="w-full accent-gold-primary cursor-pointer" />
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-300 font-mono">ECHO-1 ➔ NEXUS-3</span>
                <span className="text-gold-soft font-mono">{(echoToNexus * 100).toFixed(0)}%</span>
              </div>
              <input type="range" min="0" max="1" step="0.01" value={echoToNexus} onChange={e => setEchoToNexus(parseFloat(e.target.value))} className="w-full accent-gold-primary cursor-pointer" />
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-300 font-mono">ECHO-1 ➔ ARIA-7</span>
                <span className="text-gold-soft font-mono">{(echoToAria * 100).toFixed(0)}%</span>
              </div>
              <input type="range" min="0" max="1" step="0.01" value={echoToAria} onChange={e => setEchoToAria(parseFloat(e.target.value))} className="w-full accent-gold-primary cursor-pointer" />
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-300 font-mono">ARIA-7 ➔ ECHO-1</span>
                <span className="text-gold-soft font-mono">{(ariaToEcho * 100).toFixed(0)}%</span>
              </div>
              <input type="range" min="0" max="1" step="0.01" value={ariaToEcho} onChange={e => setAriaToEcho(parseFloat(e.target.value))} className="w-full accent-gold-primary cursor-pointer" />
            </div>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-gold-primary/10 flex items-center gap-2 text-[10px] text-gray-500 font-mono">
          <ShieldAlert size={12} className="text-danger" />
          <span>Lowering trust below 60% increases conflict probability.</span>
        </div>
      </GlassCard>
    </div>
  );
};

export default TrustGraph;


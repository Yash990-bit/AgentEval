"use client";

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { GlassCard } from '@/components/ui/GlassCard';
import { Bot, HelpCircle, Monitor } from 'lucide-react';

interface ScreenInfo {
  name: string;
  title: string;
  htmlCode?: { downloadUrl: string };
  screenshot?: { name: string; downloadUrl: string };
  width?: string;
  height?: string;
  deviceType?: string;
}

const fallbackScreens: ScreenInfo[] = [
  { name: "dashboard", title: "Main Operations Dashboard", deviceType: "Desktop" },
  { name: "simulation-studio", title: "Simulation Flow Designer", deviceType: "Desktop" },
  { name: "agents", title: "Agent Swarm Configuration", deviceType: "Desktop" },
  { name: "agent-network", title: "Affinity Communication Map", deviceType: "Desktop" },
  { name: "analytics", title: "Metrics & Goal Telemetry", deviceType: "Desktop" },
  { name: "replay", title: "Historic Session Scrubber", deviceType: "Desktop" },
];

export default function ScreensIndex() {
  const [screens, setScreens] = useState<ScreenInfo[]>([]);

  useEffect(() => {
    fetch('/screens_data.json')
      .then((res) => res.json())
      .then((data) => {
        if (data && data.screens && data.screens.length > 0) {
          setScreens(data.screens);
        } else {
          setScreens(fallbackScreens);
        }
      })
      .catch((err) => {
        console.warn("Could not load screens data, utilizing fallback index.", err);
        setScreens(fallbackScreens);
      });
  }, []);

  return (
    <div className="p-8">
      <GlassCard className="p-8">
        <h3 className="text-2xl font-bold mb-4 text-gold-primary flex items-center gap-2">
          <Monitor size={24} />
          Stitch Interface Templates
        </h3>
        <p className="text-sm text-gray-400 mb-6">Explore the full layout library and design view templates generated for the simulation environment.</p>

        <ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {screens.map((screen) => {
            const slug = screen.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
            return (
              <li key={screen.name}>
                <Link
                  href={`/screens/${slug}`}
                  className="block p-4 border border-gold-primary/10 rounded-lg bg-black/40 hover:border-gold-primary/30 transition-all hover:scale-[1.02]"
                >
                  {screen.screenshot ? (
                    <img src={screen.screenshot.downloadUrl} alt={screen.title} className="w-full h-40 object-cover rounded border border-white/5" />
                  ) : (
                    <div className="w-full h-40 bg-gold-primary/5 border border-dashed border-gold-primary/10 rounded flex flex-col items-center justify-center text-gold-primary opacity-60">
                      <Bot size={32} className="mb-2" />
                      <span className="text-xs uppercase tracking-wider font-mono">Preset Frame</span>
                    </div>
                  )}
                  <h4 className="mt-3 text-lg font-medium text-white text-center">{screen.title}</h4>
                  <p className="text-xs text-center text-gray-500 mt-1 font-mono">{screen.deviceType || 'Responsive'}</p>
                </Link>
              </li>
            );
          })}
        </ul>
      </GlassCard>
    </div>
  );
}

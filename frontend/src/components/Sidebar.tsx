"use client";
import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  FlaskRound,
  Bot,
  Network,
  BarChart3,
  PlayCircle,
  Settings,
  User,
  Shield,
  TrendingUp,
} from 'lucide-react';

const navItems = [
  { id: 'dashboard', href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'simulation-studio', href: '/simulation-studio', label: 'Simulation Studio', icon: FlaskRound },
  { id: 'agents', href: '/agents', label: 'Agent Management', icon: Bot },
  { id: 'agent-network', href: '/agent-network', label: 'Agent Network', icon: Network },
  { id: 'analytics', href: '/analytics', label: 'Analytics', icon: BarChart3 },
  { id: 'predictions', href: '/predictions', label: 'Predictions', icon: TrendingUp },
  { id: 'trust', href: '/trust', label: 'Trust Network', icon: Shield },
  { id: 'replay', href: '/replay', label: 'Replay Center', icon: PlayCircle },
  { id: 'settings', href: '/settings', label: 'Settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-full w-60 bg-black/70 backdrop-blur-md flex flex-col justify-between p-4 z-40 border-r border-gold-primary/10">
      <div>
        <Link href="/">
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gold-primary to-gold-secondary mb-8 cursor-pointer">
            AgentVerse
          </h1>
        </Link>
        <nav className="flex flex-col gap-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href;
            return (
              <Link
                key={item.id}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded transition-colors ${
                  active
                    ? 'bg-gold-primary text-black font-semibold border-l-4 border-gold-secondary'
                    : 'text-gray-300 hover:bg-gold-primary/10'
                }`}
              >
                <Icon size={20} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
      <div className="flex items-center gap-2 text-gray-400">
        <User size={20} />
        <span>Yash • <span className="text-gold-primary">● LIVE</span></span>
      </div>
    </aside>
  );
};

export default Sidebar;

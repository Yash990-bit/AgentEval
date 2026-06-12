"use client";
import React from 'react';
import { usePathname } from 'next/navigation';
import { Bell, User } from 'lucide-react';
import { GoldButton } from './ui/GoldButton';

export const Header: React.FC = () => {
  const pathname = usePathname();

  const titles: Record<string, string> = {
    '/': 'Dashboard',
    '/simulation-studio': 'Simulation Studio',
    '/agents': 'Agent Management',
    '/agent-network': 'Agent Network',
    '/analytics': 'Analytics',
    '/predictions': 'Predictions Dashboard',
    '/trust': 'Trust Network',
    '/replay': 'Replay Center',
    '/settings': 'Settings',
  };

  const title = titles[pathname] || 'AgentVerse';

  return (
    <header className="fixed left-60 top-0 right-0 h-16 bg-black/80 backdrop-blur-md flex items-center justify-between px-6 z-30 border-b border-gold-primary/10">
      <h2 className="text-xl font-medium text-gold-primary">{title}</h2>
      <div className="flex items-center gap-4">
        <div className="relative">
          <Bell size={20} className="text-gray-400" />
          <span className="absolute -top-1 -right-1 w-2 h-2 bg-gold-primary rounded-full animate-pulse"></span>
        </div>
        <GoldButton variant="primary" onClick={() => alert('New simulation started')}>
          New Simulation
        </GoldButton>
        <User size={20} className="text-gray-400" />
      </div>
    </header>
  );
};

export default Header;

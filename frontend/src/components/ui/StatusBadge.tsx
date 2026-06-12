import React from 'react';

interface StatusBadgeProps {
  status: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const colors: Record<string, string> = {
    running: 'bg-success',
    paused: 'bg-warning',
    completed: 'bg-gray-500',
    failed: 'bg-danger',
    critical: 'bg-danger',
    high: 'bg-danger',
    medium: 'bg-warning',
    low: 'bg-success',
  };
  const bg = colors[status.toLowerCase()] || 'bg-gray-500';
  return <span className={`px-2 py-1 text-xs rounded ${bg} text-black font-semibold`}>{status}</span>;
};

export default StatusBadge;

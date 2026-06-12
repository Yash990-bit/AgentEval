import React from 'react';

export const AgentCard: React.FC<{ id: string; role: string; name: string }> = ({ id, role, name }) => {
  return (
    <div
      id={id}
      className="agent-card p-2 border rounded cursor-grab bg-[var(--card)] text-[var(--white)] hover:bg-[var(--surface)]"
      data-id={id}
      data-role={role}
      data-name={name}
    >
      <strong>{name}</strong>
      <br />
      <small>{role}</small>
    </div>
  );
};

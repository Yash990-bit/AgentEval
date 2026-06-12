"use client";
import React from 'react';

interface GoldButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'outline';
}

export const GoldButton: React.FC<GoldButtonProps> = ({ variant = 'primary', children, className = '', ...props }) => {
  const baseClassName = `btn ${variant === 'primary' ? 'btn-primary' : 'btn-outline'} ${className}`;
  return (
    <button className={baseClassName} {...props}>
      {children}
    </button>
  );
};

export default GoldButton;

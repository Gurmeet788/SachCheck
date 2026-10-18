import React from 'react';

/**
 * StatusBadge component
 * @param {{ status: string, size?: 'sm' | 'md' | 'lg' }} props
 */
export default function StatusBadge({ status, size = 'md' }) {
  const isFactChecked = status === 'fact_checked';

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1.5',
    md: 'text-xs px-3 py-1 gap-2 font-medium',
    lg: 'text-sm px-4 py-1.5 gap-2 font-semibold',
  }[size] || 'text-xs px-3 py-1 gap-2';

  if (isFactChecked) {
    return (
      <span
        id="badge-status-fact-checked"
        className={`inline-flex items-center rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 ${sizeClasses}`}
      >
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        <span>Fact Checked</span>
      </span>
    );
  }

  return (
    <span
      id="badge-status-unverified"
      className={`inline-flex items-center rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30 ${sizeClasses}`}
    >
      <span className="w-2 h-2 rounded-full bg-amber-400" />
      <span>Unverified / No Matches</span>
    </span>
  );
}

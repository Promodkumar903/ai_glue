import React from 'react';

const GRADE_STYLES = {
  A: {
    bg: 'bg-gradient-to-r from-yellow-400 to-yellow-600',
    text: 'text-white',
    border: 'border-yellow-300',
    label: 'Elite',
    emoji: '⭐',
  },
  B: {
    bg: 'bg-gradient-to-r from-slate-300 to-slate-500',
    text: 'text-white',
    border: 'border-slate-200',
    label: 'Trusted',
    emoji: '✨',
  },
  C: {
    bg: 'bg-gradient-to-r from-amber-600 to-amber-800',
    text: 'text-white',
    border: 'border-amber-400',
    label: 'Verified',
    emoji: '✓',
  },
  D: {
    bg: 'bg-gray-500',
    text: 'text-white',
    border: 'border-gray-400',
    label: 'Standard',
    emoji: '',
  },
  E: {
    bg: 'bg-red-600',
    text: 'text-white',
    border: 'border-red-400',
    label: 'Probation',
    emoji: '⚠',
  },
};

const TREND_ICONS = {
  up: '↑',
  down: '↓',
  stable: '→',
};

export default function GradeBadge({ grade, trend, size = 'md', showLabel = false }) {
  if (!grade) {
    return (
      <span className="inline-flex items-center px-2 py-1 rounded-md bg-gray-200 text-gray-500 text-xs font-medium">
        No Grade
      </span>
    );
  }

  const style = GRADE_STYLES[grade] || GRADE_STYLES.E;
  const trendIcon = trend ? TREND_ICONS[trend] : null;

  const sizes = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-1.5',
  };

  const trendColor =
    trend === 'up' ? 'text-green-300' :
    trend === 'down' ? 'text-red-300' :
    'text-white opacity-70';

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-md font-bold shadow-sm border ${style.bg} ${style.text} ${style.border} ${sizes[size] || sizes.md}`}
      title={`Grade ${grade} — ${style.label}`}
    >
      <span>{style.emoji}{grade}</span>
      {showLabel && <span className="font-medium opacity-90">{style.label}</span>}
      {trendIcon && <span className={`text-xs ${trendColor}`}>{trendIcon}</span>}
    </span>
  );
}
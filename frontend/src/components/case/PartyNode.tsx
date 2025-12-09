/**
 * Custom React Flow Node for Party
 * 009-calm-control-design-system
 */

'use client';

import { memo } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import type { Party, PartyType } from '@/types/relations';

// Party type labels in Korean
const PARTY_LABELS: Record<PartyType, string> = {
  plaintiff: '원고',
  defendant: '피고',
  child: '자녀',
  third_party: '제3자',
};

// Party type icons (simple SVG)
const PartyIcon = ({ type }: { type: PartyType }) => {
  if (type === 'child') {
    return (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    );
  }
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
    </svg>
  );
};

interface PartyNodeData {
  label: string;
  party: Party;
  colors: { bg: string; border: string };
}

function PartyNodeComponent({ data, selected }: NodeProps<PartyNodeData>) {
  const { party, colors } = data;

  return (
    <div
      className={`
        px-4 py-3 rounded-lg min-w-[120px] text-center
        transition-shadow duration-200
        ${selected ? 'shadow-lg ring-2 ring-offset-2' : 'shadow-sm hover:shadow-md'}
      `}
      style={{
        backgroundColor: colors.bg,
        borderWidth: '2px',
        borderStyle: 'solid',
        borderColor: colors.border,
        ringColor: selected ? colors.border : undefined,
      }}
    >
      {/* Connection handles */}
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-neutral-400"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-neutral-400"
      />
      <Handle
        type="target"
        position={Position.Left}
        id="left-target"
        className="w-3 h-3 !bg-neutral-400"
      />
      <Handle
        type="source"
        position={Position.Right}
        id="right-source"
        className="w-3 h-3 !bg-neutral-400"
      />

      {/* Content */}
      <div className="flex flex-col items-center gap-1">
        <div
          className="flex items-center justify-center w-8 h-8 rounded-full"
          style={{ backgroundColor: colors.border, color: 'white' }}
        >
          <PartyIcon type={party.type} />
        </div>
        <div className="font-medium text-sm text-gray-900">
          {party.name}
        </div>
        <div
          className="text-xs px-2 py-0.5 rounded-full"
          style={{ backgroundColor: colors.border, color: 'white' }}
        >
          {PARTY_LABELS[party.type]}
        </div>
      </div>
    </div>
  );
}

export const PartyNode = memo(PartyNodeComponent);

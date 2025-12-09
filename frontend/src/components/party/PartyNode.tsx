/**
 * PartyNode - Custom React Flow node for party visualization
 * User Story 1: Party Relationship Graph
 */

'use client';

import { memo } from 'react';
import { Handle, Position, type Node, type NodeProps } from '@xyflow/react';
import type { PartyType } from '@/types/party';
import { PARTY_TYPE_LABELS } from '@/types/party';

export interface PartyNodeData {
  id: string;
  name: string;
  type: PartyType;
  alias?: string;
  occupation?: string;
  birth_year?: number;
  evidenceCount?: number;
  onEdit?: (id: string) => void;
  onDelete?: (id: string) => void;
  [key: string]: unknown;
}

export type PartyNodeType = Node<PartyNodeData, 'party'>;

// Color mapping for party types (light and dark mode)
const PARTY_COLORS: Record<PartyType, { bg: string; border: string; icon: string }> = {
  plaintiff: {
    bg: 'bg-blue-50 dark:bg-blue-900/30',
    border: 'border-blue-500',
    icon: '👤',
  },
  defendant: {
    bg: 'bg-red-50 dark:bg-red-900/30',
    border: 'border-red-500',
    icon: '👤',
  },
  third_party: {
    bg: 'bg-amber-50 dark:bg-amber-900/30',
    border: 'border-amber-500',
    icon: '👥',
  },
  child: {
    bg: 'bg-green-50 dark:bg-green-900/30',
    border: 'border-green-500',
    icon: '👶',
  },
  family: {
    bg: 'bg-purple-50 dark:bg-purple-900/30',
    border: 'border-purple-500',
    icon: '👨‍👩‍👧',
  },
};

function PartyNodeComponent({ data, selected }: NodeProps<PartyNodeType>) {
  const colors = PARTY_COLORS[data.type] || PARTY_COLORS.third_party;
  const label = PARTY_TYPE_LABELS[data.type] || data.type;

  return (
    <div
      className={`
        px-4 py-3 rounded-lg border-2 shadow-sm min-w-[140px]
        ${colors.bg} ${colors.border}
        ${selected ? 'ring-2 ring-offset-2 ring-blue-400' : ''}
        transition-shadow hover:shadow-md
      `}
    >
      {/* Connection handles */}
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 bg-gray-400 dark:bg-gray-500 border-2 border-white dark:border-gray-800"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 bg-gray-400 dark:bg-gray-500 border-2 border-white dark:border-gray-800"
      />
      <Handle
        type="target"
        position={Position.Left}
        id="left"
        className="w-3 h-3 bg-gray-400 dark:bg-gray-500 border-2 border-white dark:border-gray-800"
      />
      <Handle
        type="source"
        position={Position.Right}
        id="right"
        className="w-3 h-3 bg-gray-400 dark:bg-gray-500 border-2 border-white dark:border-gray-800"
      />

      {/* Node content */}
      <div className="flex flex-col items-center gap-1">
        {/* Type label */}
        <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
          {colors.icon} {label}
        </span>

        {/* Name */}
        <span className="text-sm font-semibold text-gray-800 dark:text-gray-100 text-center">
          {data.name}
        </span>

        {/* Alias */}
        {data.alias && (
          <span className="text-xs text-gray-500 dark:text-gray-400">({data.alias})</span>
        )}

        {/* Occupation / Birth year */}
        {(data.occupation || data.birth_year) && (
          <span className="text-xs text-gray-400 dark:text-gray-500">
            {data.occupation}
            {data.occupation && data.birth_year && ' · '}
            {data.birth_year && `${data.birth_year}년생`}
          </span>
        )}

        {/* Evidence count badge */}
        {data.evidenceCount !== undefined && data.evidenceCount > 0 && (
          <span className="mt-1 px-2 py-0.5 text-xs bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-full">
            증거 {data.evidenceCount}건
          </span>
        )}
      </div>
    </div>
  );
}

export const PartyNode = memo(PartyNodeComponent);

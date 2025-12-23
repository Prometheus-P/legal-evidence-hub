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
  // 012-precedent-integration: T048-T050 자동 추출 필드
  is_auto_extracted?: boolean;
  extraction_confidence?: number;
  source_evidence_id?: string;
  onEdit?: (id: string) => void;
  onDelete?: (id: string) => void;
  [key: string]: unknown;
}

export type PartyNodeType = Node<PartyNodeData, 'party'>;

// 012-precedent-integration: T048-T050 신뢰도 배지 색상
function getConfidenceBadgeColor(confidence: number): string {
  if (confidence >= 0.9) return 'bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-300';
  if (confidence >= 0.7) return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/50 dark:text-yellow-300';
  return 'bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300';
}

// Color mapping for party types - 이미지 기준 색상
const PARTY_COLORS: Record<PartyType, { bg: string; border: string; text: string; initial: string }> = {
  plaintiff: {
    bg: 'bg-emerald-100 dark:bg-emerald-900/40',
    border: 'border-emerald-400 dark:border-emerald-500',
    text: 'text-emerald-700 dark:text-emerald-300',
    initial: 'bg-emerald-500 dark:bg-emerald-600',
  },
  defendant: {
    bg: 'bg-pink-100 dark:bg-pink-900/40',
    border: 'border-pink-400 dark:border-pink-500',
    text: 'text-pink-700 dark:text-pink-300',
    initial: 'bg-pink-500 dark:bg-pink-600',
  },
  third_party: {
    bg: 'bg-emerald-100 dark:bg-emerald-900/40',
    border: 'border-emerald-400 dark:border-emerald-500',
    text: 'text-emerald-700 dark:text-emerald-300',
    initial: 'bg-emerald-500 dark:bg-emerald-600',
  },
  child: {
    bg: 'bg-sky-100 dark:bg-sky-900/40',
    border: 'border-sky-400 dark:border-sky-500',
    text: 'text-sky-700 dark:text-sky-300',
    initial: 'bg-sky-500 dark:bg-sky-600',
  },
  family: {
    bg: 'bg-gray-100 dark:bg-gray-800',
    border: 'border-gray-300 dark:border-gray-600',
    text: 'text-gray-600 dark:text-gray-400',
    initial: 'bg-gray-400 dark:bg-gray-500',
  },
};

// 이름에서 이니셜 추출 (성만 가져오기)
function getInitial(name: string): string {
  if (!name) return '?';
  return name.charAt(0);
}

function PartyNodeComponent({ data, selected }: NodeProps<PartyNodeType>) {
  const colors = PARTY_COLORS[data.type] || PARTY_COLORS.third_party;
  const label = PARTY_TYPE_LABELS[data.type] || data.type;
  const initial = getInitial(data.name);

  return (
    <div
      className={`
        flex flex-col items-center gap-2 p-3
        ${selected ? 'scale-105' : ''}
        transition-transform
      `}
    >
      {/* Connection handles - 투명하게 처리 */}
      <Handle
        type="target"
        position={Position.Top}
        className="w-2 h-2 !bg-transparent !border-0"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-2 h-2 !bg-transparent !border-0"
      />
      <Handle
        type="target"
        position={Position.Left}
        id="left"
        className="w-2 h-2 !bg-transparent !border-0"
      />
      <Handle
        type="source"
        position={Position.Right}
        id="right"
        className="w-2 h-2 !bg-transparent !border-0"
      />

      {/* 원형 이니셜 아바타 */}
      <div
        className={`
          w-12 h-12 rounded-full flex items-center justify-center
          ${colors.initial} text-white text-lg font-bold
          shadow-md
          ${selected ? 'ring-2 ring-offset-2 ring-blue-400 dark:ring-offset-neutral-900' : ''}
        `}
      >
        {initial}
      </div>

      {/* 이름 */}
      <div className="flex flex-col items-center">
        <span className="text-sm font-semibold text-gray-800 dark:text-gray-100 whitespace-nowrap">
          {data.name}
        </span>
        {/* 역할 라벨 */}
        <span className={`text-xs ${colors.text}`}>
          {label}
        </span>
      </div>

      {/* 012-precedent-integration: AI 자동 추출 배지 */}
      {data.is_auto_extracted && (
        <span
          className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${getConfidenceBadgeColor(data.extraction_confidence || 0.7)}`}
          title={`AI 자동 추출 (신뢰도: ${Math.round((data.extraction_confidence || 0.7) * 100)}%)`}
        >
          🤖 {Math.round((data.extraction_confidence || 0.7) * 100)}%
        </span>
      )}
    </div>
  );
}

export const PartyNode = memo(PartyNodeComponent);

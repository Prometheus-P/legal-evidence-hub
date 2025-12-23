/**
 * PartyEdge - Custom React Flow edge for relationship visualization
 * User Story 1: Party Relationship Graph
 */

'use client';

import { memo } from 'react';
import {
  BaseEdge,
  EdgeLabelRenderer,
  getBezierPath,
  type Edge,
  type EdgeProps,
} from '@xyflow/react';
import type { RelationshipType } from '@/types/party';
import { RELATIONSHIP_TYPE_LABELS } from '@/types/party';

export interface PartyEdgeData {
  type: RelationshipType;
  start_date?: string;
  end_date?: string;
  notes?: string;
  // 012-precedent-integration: T048-T050 자동 추출 필드
  is_auto_extracted?: boolean;
  extraction_confidence?: number;
  evidence_text?: string;
  onClick?: (id: string) => void;
  [key: string]: unknown;
}

export type PartyEdgeType = Edge<PartyEdgeData, 'relationship'>;

// Style mapping for relationship types - 이미지 기준 스타일
const RELATIONSHIP_STYLES: Record<RelationshipType, {
  stroke: string;
  strokeDasharray?: string;
  strokeWidth: number;
}> = {
  marriage: {
    stroke: '#3B82F6', // blue-500
    strokeWidth: 2,
  },
  affair: {
    stroke: '#EC4899', // pink-500 (이미지 기준)
    strokeDasharray: '6,4',
    strokeWidth: 2,
  },
  parent_child: {
    stroke: '#10B981', // emerald-500
    strokeWidth: 2,
  },
  sibling: {
    stroke: '#6B7280', // gray-500
    strokeDasharray: '4,4',
    strokeWidth: 1.5,
  },
  in_law: {
    stroke: '#8B5CF6', // violet-500
    strokeDasharray: '6,3',
    strokeWidth: 1.5,
  },
  cohabit: {
    stroke: '#F59E0B', // amber-500
    strokeDasharray: '8,4',
    strokeWidth: 2,
  },
  relative: {
    stroke: '#94A3B8', // slate-400
    strokeDasharray: '3,3',
    strokeWidth: 1.5,
  },
  other: {
    stroke: '#CBD5E1', // slate-300
    strokeDasharray: '4,4',
    strokeWidth: 1.5,
  },
};

function PartyEdgeComponent({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  selected,
}: EdgeProps<PartyEdgeType>) {
  const relationshipType = data?.type || 'marriage';
  const style = RELATIONSHIP_STYLES[relationshipType] || RELATIONSHIP_STYLES.marriage;
  const typeLabel = RELATIONSHIP_TYPE_LABELS[relationshipType] || relationshipType;

  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const handleClick = () => {
    data?.onClick?.(id);
  };

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        style={{
          stroke: style.stroke,
          strokeWidth: selected ? style.strokeWidth + 1 : style.strokeWidth,
          strokeDasharray: style.strokeDasharray,
        }}
        interactionWidth={20}
      />
      <EdgeLabelRenderer>
        <div
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            pointerEvents: 'all',
          }}
          className="nodrag nopan"
        >
          <button
            onClick={handleClick}
            className={`
              px-2.5 py-1 rounded-md text-xs font-medium
              bg-white/90 dark:bg-neutral-800/90 backdrop-blur-sm
              border border-gray-200 dark:border-neutral-600
              shadow-sm hover:shadow-md transition-shadow cursor-pointer
              text-gray-600 dark:text-gray-300
              ${selected ? 'ring-2 ring-blue-400' : ''}
            `}
            title={data?.is_auto_extracted ? `AI 자동 추출 (신뢰도: ${Math.round((data.extraction_confidence || 0.7) * 100)}%)` : undefined}
          >
            {/* 012-precedent-integration: T048-T050 자동 추출 표시 */}
            {data?.is_auto_extracted && (
              <span className="mr-1 text-purple-500" title="AI 자동 추출">🤖</span>
            )}
            {typeLabel}
            {data?.notes && <span className="ml-0.5 text-gray-400">?</span>}
          </button>
        </div>
      </EdgeLabelRenderer>
    </>
  );
}

export const PartyEdge = memo(PartyEdgeComponent);

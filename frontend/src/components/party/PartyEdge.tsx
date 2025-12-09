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
  onClick?: (id: string) => void;
  [key: string]: unknown;
}

export type PartyEdgeType = Edge<PartyEdgeData, 'relationship'>;

// Style mapping for relationship types
const RELATIONSHIP_STYLES: Record<RelationshipType, {
  stroke: string;
  strokeDasharray?: string;
  strokeWidth: number;
  label: string;
}> = {
  marriage: {
    stroke: '#3B82F6', // blue-500
    strokeWidth: 3,
    label: '💍',
  },
  affair: {
    stroke: '#EF4444', // red-500
    strokeDasharray: '5,5',
    strokeWidth: 2,
    label: '💔',
  },
  parent_child: {
    stroke: '#22C55E', // green-500
    strokeWidth: 2,
    label: '👶',
  },
  sibling: {
    stroke: '#6B7280', // gray-500
    strokeDasharray: '3,3',
    strokeWidth: 1,
    label: '👫',
  },
  in_law: {
    stroke: '#8B5CF6', // violet-500
    strokeDasharray: '5,3',
    strokeWidth: 1,
    label: '🤝',
  },
  cohabit: {
    stroke: '#F59E0B', // amber-500
    strokeDasharray: '8,4',
    strokeWidth: 2,
    label: '🏠',
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
              px-2 py-1 rounded-full text-xs font-medium
              bg-white dark:bg-neutral-800 border shadow-sm dark:shadow-neutral-900/50
              hover:shadow-md dark:hover:shadow-neutral-900/70 transition-shadow cursor-pointer
              text-gray-800 dark:text-gray-200
              ${selected ? 'ring-2 ring-blue-400' : ''}
            `}
            style={{ borderColor: style.stroke }}
          >
            <span className="mr-1">{style.label}</span>
            {typeLabel}
            {data?.start_date && (
              <span className="ml-1 text-gray-400 dark:text-gray-500">
                ({new Date(data.start_date).getFullYear()}~
                {data.end_date ? new Date(data.end_date).getFullYear() : ''})
              </span>
            )}
          </button>
        </div>
      </EdgeLabelRenderer>
    </>
  );
}

export const PartyEdge = memo(PartyEdgeComponent);

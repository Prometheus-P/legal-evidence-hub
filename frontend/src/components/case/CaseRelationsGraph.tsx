/**
 * Case Relations Graph Component
 * 009-calm-control-design-system - React Flow Integration
 *
 * Displays party relationships in a visual graph format.
 * Calm-Control: Clean, draggable nodes with subtle visual hierarchy.
 */

'use client';

import { useCallback, useMemo, useState } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  NodeTypes,
  BackgroundVariant,
  Panel,
  Node,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { PartyNode } from './PartyNode';
import { useCaseRelations, PARTY_COLORS } from '@/hooks/useCaseRelations';
import type { Party, PartyType, RelationType } from '@/types/relations';

// Register custom node types
const nodeTypes: NodeTypes = {
  // Type assertion needed due to ReactFlow v12 stricter typing
  partyNode: PartyNode as NodeTypes[string],
};

// Relation type options for creating new relations
const RELATION_OPTIONS: { value: RelationType; label: string }[] = [
  { value: 'marriage', label: '혼인' },
  { value: 'parent_child', label: '친자' },
  { value: 'affair', label: '불륜' },
  { value: 'relative', label: '친족' },
  { value: 'other', label: '기타' },
];

// Party type options for creating new parties
const PARTY_OPTIONS: { value: PartyType; label: string }[] = [
  { value: 'plaintiff', label: '원고' },
  { value: 'defendant', label: '피고' },
  { value: 'child', label: '자녀' },
  { value: 'third_party', label: '제3자' },
];

interface CaseRelationsGraphProps {
  caseId: string;
  readOnly?: boolean;
}

export function CaseRelationsGraph({ caseId, readOnly = false }: CaseRelationsGraphProps) {
  const {
    nodes: initialNodes,
    edges: initialEdges,
    isLoading,
    error,
    selectedParty,
    setSelectedParty,
    savePositions,
    addParty,
    removeParty,
    addRelation,
    removeRelation,
  } = useCaseRelations({ caseId });

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [showAddParty, setShowAddParty] = useState(false);
  const [newPartyName, setNewPartyName] = useState('');
  const [newPartyType, setNewPartyType] = useState<PartyType>('plaintiff');
  const [connectingRelationType, setConnectingRelationType] = useState<RelationType>('marriage');

  // Sync nodes when initial data changes
  useMemo(() => {
    if (initialNodes.length > 0) {
      setNodes(initialNodes);
    }
  }, [initialNodes, setNodes]);

  useMemo(() => {
    if (initialEdges.length > 0) {
      setEdges(initialEdges);
    }
  }, [initialEdges, setEdges]);

  // Handle node drag end - save positions
  const onNodeDragStop = useCallback(
    (_event: React.MouseEvent, _node: unknown, draggedNodes: unknown[]) => {
      if (!readOnly) {
        savePositions(draggedNodes as Node[]);
      }
    },
    [readOnly, savePositions]
  );

  // Handle new connection (creating relation)
  const onConnect = useCallback(
    (connection: Connection) => {
      if (readOnly || !connection.source || !connection.target) return;

      // Add the relation
      addRelation({
        source_party_id: connection.source,
        target_party_id: connection.target,
        relation_type: connectingRelationType,
      }).then(() => {
        setEdges((eds) =>
          addEdge(
            {
              ...connection,
              type: 'default',
              label: RELATION_OPTIONS.find((r) => r.value === connectingRelationType)?.label,
            },
            eds
          )
        );
      });
    },
    [readOnly, addRelation, connectingRelationType, setEdges]
  );

  // Handle node click - show party details
  const onNodeClick = useCallback(
    (_event: React.MouseEvent, node: unknown) => {
      const typedNode = node as { data?: { party?: Party } };
      if (typedNode.data?.party) {
        setSelectedParty(typedNode.data.party);
      }
    },
    [setSelectedParty]
  );

  // Add new party
  const handleAddParty = useCallback(async () => {
    if (!newPartyName.trim()) return;

    try {
      await addParty({
        name: newPartyName,
        type: newPartyType,
        position_x: 200 + Math.random() * 200,
        position_y: 200 + Math.random() * 200,
      });
      setNewPartyName('');
      setShowAddParty(false);
    } catch (err) {
      console.error('Failed to add party:', err);
    }
  }, [newPartyName, newPartyType, addParty]);

  // Delete selected party
  const handleDeleteParty = useCallback(async () => {
    if (!selectedParty) return;

    if (confirm(`"${selectedParty.name}" 당사자를 삭제하시겠습니까?`)) {
      try {
        await removeParty(selectedParty.id);
        setSelectedParty(null);
      } catch (err) {
        console.error('Failed to delete party:', err);
      }
    }
  }, [selectedParty, removeParty, setSelectedParty]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[500px] bg-neutral-50 rounded-lg">
        <div className="text-neutral-500">관계도 불러오는 중...</div>
      </div>
    );
  }

  if (error && nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-[500px] bg-neutral-50 rounded-lg">
        <div className="text-center">
          <p className="text-neutral-500 mb-2">{error}</p>
          <p className="text-sm text-neutral-400">샘플 데이터로 표시합니다.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-[600px] bg-neutral-50 rounded-lg border border-neutral-200">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeDragStop={onNodeDragStop}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.5}
        maxZoom={2}
        defaultEdgeOptions={{
          type: 'smoothstep',
          animated: false,
        }}
        proOptions={{ hideAttribution: true }}
      >
        <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#CBD5E1" />
        <Controls showInteractive={false} />
        <MiniMap
          nodeColor={(node) => {
            const party = node.data?.party as Party | undefined;
            return party ? PARTY_COLORS[party.type].border : '#94A3B8';
          }}
          maskColor="rgba(0, 0, 0, 0.1)"
          className="!bg-white !border-neutral-200"
        />

        {/* Control Panel */}
        {!readOnly && (
          <Panel position="top-left" className="space-y-2">
            {/* Relation type selector for new connections */}
            <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-3">
              <label className="block text-xs text-neutral-500 mb-1">연결 시 관계 유형</label>
              <select
                value={connectingRelationType}
                onChange={(e) => setConnectingRelationType(e.target.value as RelationType)}
                className="w-full text-sm border border-neutral-200 rounded px-2 py-1"
              >
                {RELATION_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Add party button */}
            {!showAddParty ? (
              <button
                onClick={() => setShowAddParty(true)}
                className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-hover transition-colors"
              >
                + 당사자 추가
              </button>
            ) : (
              <div className="bg-white rounded-lg shadow-sm border border-neutral-200 p-3 space-y-2">
                <input
                  type="text"
                  value={newPartyName}
                  onChange={(e) => setNewPartyName(e.target.value)}
                  placeholder="이름 입력"
                  className="w-full text-sm border border-neutral-200 rounded px-2 py-1"
                  autoFocus
                />
                <select
                  value={newPartyType}
                  onChange={(e) => setNewPartyType(e.target.value as PartyType)}
                  className="w-full text-sm border border-neutral-200 rounded px-2 py-1"
                >
                  {PARTY_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
                <div className="flex gap-2">
                  <button
                    onClick={handleAddParty}
                    className="flex-1 bg-primary text-white px-3 py-1 rounded text-sm hover:bg-primary-hover"
                  >
                    추가
                  </button>
                  <button
                    onClick={() => setShowAddParty(false)}
                    className="flex-1 bg-neutral-100 text-neutral-600 px-3 py-1 rounded text-sm hover:bg-neutral-200"
                  >
                    취소
                  </button>
                </div>
              </div>
            )}
          </Panel>
        )}

        {/* Selected Party Panel */}
        {selectedParty && (
          <Panel position="top-right" className="bg-white rounded-lg shadow-lg border border-neutral-200 p-4 w-64">
            <div className="flex items-start justify-between mb-3">
              <h3 className="font-medium text-gray-900">{selectedParty.name}</h3>
              <button
                onClick={() => setSelectedParty(null)}
                className="text-neutral-400 hover:text-neutral-600"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-neutral-500">유형: </span>
                <span className="font-medium">
                  {PARTY_OPTIONS.find((p) => p.value === selectedParty.type)?.label}
                </span>
              </div>
              {selectedParty.description && (
                <div>
                  <span className="text-neutral-500">설명: </span>
                  <span>{selectedParty.description}</span>
                </div>
              )}
              {selectedParty.birth_date && (
                <div>
                  <span className="text-neutral-500">생년월일: </span>
                  <span>{selectedParty.birth_date}</span>
                </div>
              )}
            </div>
            {!readOnly && (
              <div className="mt-4 pt-3 border-t border-neutral-200">
                <button
                  onClick={handleDeleteParty}
                  className="w-full text-sm text-error hover:bg-error-light px-3 py-2 rounded transition-colors"
                >
                  당사자 삭제
                </button>
              </div>
            )}
          </Panel>
        )}

        {/* Legend */}
        <Panel position="bottom-left" className="bg-white/90 rounded-lg shadow-sm border border-neutral-200 p-3">
          <div className="text-xs text-neutral-500 mb-2 font-medium">범례</div>
          <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
            {PARTY_OPTIONS.map((opt) => (
              <div key={opt.value} className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: PARTY_COLORS[opt.value].border }}
                />
                <span>{opt.label}</span>
              </div>
            ))}
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
}

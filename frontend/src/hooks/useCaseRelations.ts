/**
 * Hook for Case Relations Graph
 * 009-calm-control-design-system
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import type { Node, Edge } from '@xyflow/react';
import type { Party, Relation, PartyType, RelationType, CaseGraphData } from '@/types/relations';
import * as relationsApi from '@/lib/api/relations';

// Node/Edge style configuration based on design system
const PARTY_COLORS: Record<PartyType, { bg: string; border: string }> = {
  plaintiff: { bg: 'rgba(26, 188, 156, 0.1)', border: '#1ABC9C' }, // primary-light
  defendant: { bg: 'rgba(44, 62, 80, 0.1)', border: '#2C3E50' }, // secondary-light
  child: { bg: 'rgba(46, 204, 113, 0.1)', border: '#2ECC71' }, // success-light
  third_party: { bg: 'rgba(243, 156, 18, 0.1)', border: '#F39C12' }, // warning-light
};

const RELATION_STYLES: Record<RelationType, { stroke: string; strokeDasharray?: string; label: string }> = {
  marriage: { stroke: '#1ABC9C', label: '혼인' },
  parent_child: { stroke: '#64748B', label: '친자' },
  affair: { stroke: '#E74C3C', strokeDasharray: '5,5', label: '불륜' },
  relative: { stroke: '#94A3B8', strokeDasharray: '2,2', label: '친족' },
  other: { stroke: '#CBD5E1', label: '기타' },
};

// Convert Party to React Flow Node
function partyToNode(party: Party): Node {
  const colors = PARTY_COLORS[party.type];
  return {
    id: party.id,
    type: 'partyNode',
    position: { x: party.position_x || 0, y: party.position_y || 0 },
    data: {
      label: party.name,
      party,
      colors,
    },
  };
}

// Convert Relation to React Flow Edge
function relationToEdge(relation: Relation): Edge {
  const style = RELATION_STYLES[relation.relation_type];
  return {
    id: relation.id,
    source: relation.source_party_id,
    target: relation.target_party_id,
    type: 'relationEdge',
    data: {
      relation,
      style,
    },
    style: {
      stroke: style.stroke,
      strokeDasharray: style.strokeDasharray,
    },
    label: relation.label || style.label,
    labelStyle: { fill: '#64748B', fontSize: 12 },
  };
}

interface UseCaseRelationsOptions {
  caseId: string;
  autoSavePositions?: boolean;
}

export function useCaseRelations({ caseId, autoSavePositions = true }: UseCaseRelationsOptions) {
  const [parties, setParties] = useState<Party[]>([]);
  const [relations, setRelations] = useState<Relation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedParty, setSelectedParty] = useState<Party | null>(null);
  const [selectedRelation, setSelectedRelation] = useState<Relation | null>(null);

  // Convert to React Flow nodes/edges
  const nodes = useMemo(() => parties.map(partyToNode), [parties]);
  const edges = useMemo(() => relations.map(relationToEdge), [relations]);

  // Fetch data
  const fetchData = useCallback(async () => {
    if (!caseId) return;

    setIsLoading(true);
    setError(null);

    try {
      const data = await relationsApi.getCaseGraphData(caseId);
      setParties(data.parties);
      setRelations(data.relations);
    } catch (err) {
      console.error('Failed to fetch case relations:', err);
      setError('관계 데이터를 불러오는데 실패했습니다.');
      // Set mock data for development
      setParties([
        {
          id: 'p1',
          case_id: caseId,
          name: '원고 (김OO)',
          type: 'plaintiff',
          position_x: 100,
          position_y: 100,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 'p2',
          case_id: caseId,
          name: '피고 (이OO)',
          type: 'defendant',
          position_x: 400,
          position_y: 100,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 'p3',
          case_id: caseId,
          name: '자녀 (김OO)',
          type: 'child',
          position_x: 250,
          position_y: 250,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ]);
      setRelations([
        {
          id: 'r1',
          case_id: caseId,
          source_party_id: 'p1',
          target_party_id: 'p2',
          relation_type: 'marriage',
          label: '혼인 (2015.03)',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 'r2',
          case_id: caseId,
          source_party_id: 'p1',
          target_party_id: 'p3',
          relation_type: 'parent_child',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 'r3',
          case_id: caseId,
          source_party_id: 'p2',
          target_party_id: 'p3',
          relation_type: 'parent_child',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Node position change handler (for drag)
  const onNodesChange = useCallback((changes: unknown[]) => {
    // Handle position changes from React Flow
    // This will be called during drag operations
  }, []);

  // Save positions when nodes are moved
  const savePositions = useCallback(async (updatedNodes: Node[]) => {
    if (!autoSavePositions) return;

    const positions = updatedNodes.map((node) => ({
      id: node.id,
      position_x: node.position.x,
      position_y: node.position.y,
    }));

    try {
      await relationsApi.updatePartyPositions(caseId, positions);
      // Update local state
      setParties((prev) =>
        prev.map((party) => {
          const pos = positions.find((p) => p.id === party.id);
          return pos
            ? { ...party, position_x: pos.position_x, position_y: pos.position_y }
            : party;
        })
      );
    } catch (err) {
      console.error('Failed to save positions:', err);
    }
  }, [caseId, autoSavePositions]);

  // CRUD operations
  const addParty = useCallback(async (data: Omit<Party, 'id' | 'case_id' | 'created_at' | 'updated_at'>) => {
    try {
      const newParty = await relationsApi.createParty(caseId, data);
      setParties((prev) => [...prev, newParty]);
      return newParty;
    } catch (err) {
      console.error('Failed to create party:', err);
      throw err;
    }
  }, [caseId]);

  const updateParty = useCallback(async (partyId: string, data: Partial<Party>) => {
    try {
      const updated = await relationsApi.updateParty(caseId, partyId, data);
      setParties((prev) => prev.map((p) => (p.id === partyId ? updated : p)));
      return updated;
    } catch (err) {
      console.error('Failed to update party:', err);
      throw err;
    }
  }, [caseId]);

  const removeParty = useCallback(async (partyId: string) => {
    try {
      await relationsApi.deleteParty(caseId, partyId);
      setParties((prev) => prev.filter((p) => p.id !== partyId));
      // Also remove related relations
      setRelations((prev) =>
        prev.filter((r) => r.source_party_id !== partyId && r.target_party_id !== partyId)
      );
    } catch (err) {
      console.error('Failed to delete party:', err);
      throw err;
    }
  }, [caseId]);

  const addRelation = useCallback(async (data: Omit<Relation, 'id' | 'case_id' | 'created_at' | 'updated_at'>) => {
    try {
      const newRelation = await relationsApi.createRelation(caseId, data);
      setRelations((prev) => [...prev, newRelation]);
      return newRelation;
    } catch (err) {
      console.error('Failed to create relation:', err);
      throw err;
    }
  }, [caseId]);

  const removeRelation = useCallback(async (relationId: string) => {
    try {
      await relationsApi.deleteRelation(caseId, relationId);
      setRelations((prev) => prev.filter((r) => r.id !== relationId));
    } catch (err) {
      console.error('Failed to delete relation:', err);
      throw err;
    }
  }, [caseId]);

  return {
    // Data
    parties,
    relations,
    nodes,
    edges,

    // State
    isLoading,
    error,
    selectedParty,
    selectedRelation,

    // Setters
    setSelectedParty,
    setSelectedRelation,

    // Actions
    fetchData,
    savePositions,
    addParty,
    updateParty,
    removeParty,
    addRelation,
    removeRelation,
    onNodesChange,
  };
}

// Export style constants for custom nodes/edges
export { PARTY_COLORS, RELATION_STYLES };

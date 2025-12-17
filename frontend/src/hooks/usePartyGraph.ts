/**
 * usePartyGraph hook for LEH Lawyer Portal v1
 * User Story 1: Party Relationship Graph
 *
 * Manages party graph state and operations with auto-save
 */

'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import type {
  PartyNode,
  PartyNodeCreate,
  PartyNodeUpdate,
  PartyRelationship,
  RelationshipCreate,
  RelationshipUpdate,
  PartyGraphData,
} from '@/types/party';
import {
  getPartyGraph,
  createParty,
  updateParty,
  deleteParty,
  createRelationship,
  updateRelationship,
  deleteRelationship,
} from '@/lib/api/party';

export type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

interface UsePartyGraphReturn {
  // Data
  nodes: PartyNode[];
  relationships: PartyRelationship[];
  isLoading: boolean;
  error: string | null;
  saveStatus: SaveStatus;

  // Node operations
  addNode: (data: PartyNodeCreate) => Promise<PartyNode | null>;
  updateNode: (nodeId: string, data: PartyNodeUpdate) => Promise<PartyNode | null>;
  deleteNode: (nodeId: string) => Promise<boolean>;

  // Relationship operations
  addRelationship: (data: RelationshipCreate) => Promise<PartyRelationship | null>;
  updateRelationshipData: (relationshipId: string, data: RelationshipUpdate) => Promise<PartyRelationship | null>;
  deleteRelationshipById: (relationshipId: string) => Promise<boolean>;

  // Position updates (auto-save with debounce)
  updateNodePosition: (nodeId: string, position: { x: number; y: number }) => void;

  // Refresh
  refresh: () => Promise<void>;
}

const AUTO_SAVE_DELAY = 2000; // 2 seconds debounce for position updates

export function usePartyGraph(caseId: string): UsePartyGraphReturn {
  const [nodes, setNodes] = useState<PartyNode[]>([]);
  const [relationships, setRelationships] = useState<PartyRelationship[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');

  // Pending position updates for debounced auto-save
  const pendingPositions = useRef<Map<string, { x: number; y: number }>>(new Map());
  const saveTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Fetch graph data
  const fetchGraph = useCallback(async () => {
    if (!caseId) return;

    setIsLoading(true);
    setError(null);

    try {
      const data: PartyGraphData = await getPartyGraph(caseId);
      setNodes(data.nodes || []);
      setRelationships(data.relationships || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : '관계도를 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  }, [caseId]);

  // Initial fetch
  useEffect(() => {
    fetchGraph();
  }, [fetchGraph]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, []);

  // Save pending position updates
  const savePendingPositions = useCallback(async () => {
    if (pendingPositions.current.size === 0) return;

    setSaveStatus('saving');

    const updates = Array.from(pendingPositions.current.entries());
    pendingPositions.current.clear();

    try {
      await Promise.all(
        updates.map(([nodeId, position]) =>
          updateParty(caseId, nodeId, { position })
        )
      );
      setSaveStatus('saved');
      // Reset to idle after 2 seconds
      setTimeout(() => setSaveStatus('idle'), 2000);
    } catch {
      setSaveStatus('error');
      // Restore pending positions on error for retry
      updates.forEach(([nodeId, position]) => {
        pendingPositions.current.set(nodeId, position);
      });
    }
  }, [caseId]);

  // Add node
  const addNode = useCallback(
    async (data: PartyNodeCreate): Promise<PartyNode | null> => {
      try {
        setSaveStatus('saving');
        const newNode = await createParty(caseId, data);
        setNodes((prev) => [...prev, newNode]);
        setSaveStatus('saved');
        setTimeout(() => setSaveStatus('idle'), 2000);
        return newNode;
      } catch (err) {
        setError(err instanceof Error ? err.message : '당사자 추가에 실패했습니다.');
        setSaveStatus('error');
        return null;
      }
    },
    [caseId]
  );

  // Update node
  const updateNode = useCallback(
    async (nodeId: string, data: PartyNodeUpdate): Promise<PartyNode | null> => {
      try {
        setSaveStatus('saving');
        const updated = await updateParty(caseId, nodeId, data);
        setNodes((prev) =>
          prev.map((node) => (node.id === nodeId ? updated : node))
        );
        setSaveStatus('saved');
        setTimeout(() => setSaveStatus('idle'), 2000);
        return updated;
      } catch (err) {
        setError(err instanceof Error ? err.message : '당사자 수정에 실패했습니다.');
        setSaveStatus('error');
        return null;
      }
    },
    [caseId]
  );

  // Delete node
  const deleteNode = useCallback(
    async (nodeId: string): Promise<boolean> => {
      try {
        setSaveStatus('saving');
        await deleteParty(caseId, nodeId);
        setNodes((prev) => prev.filter((node) => node.id !== nodeId));
        // Also remove relationships involving this node
        setRelationships((prev) =>
          prev.filter(
            (rel) =>
              rel.source_party_id !== nodeId && rel.target_party_id !== nodeId
          )
        );
        setSaveStatus('saved');
        setTimeout(() => setSaveStatus('idle'), 2000);
        return true;
      } catch (err) {
        setError(err instanceof Error ? err.message : '당사자 삭제에 실패했습니다.');
        setSaveStatus('error');
        return false;
      }
    },
    [caseId]
  );

  // Update node position (debounced auto-save)
  const updateNodePosition = useCallback(
    (nodeId: string, position: { x: number; y: number }) => {
      // Update local state immediately
      setNodes((prev) =>
        prev.map((node) =>
          node.id === nodeId ? { ...node, position } : node
        )
      );

      // Queue for auto-save
      pendingPositions.current.set(nodeId, position);

      // Clear existing timeout
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }

      // Set new timeout for auto-save
      saveTimeoutRef.current = setTimeout(savePendingPositions, AUTO_SAVE_DELAY);
    },
    [savePendingPositions]
  );

  // Add relationship
  const addRelationship = useCallback(
    async (data: RelationshipCreate): Promise<PartyRelationship | null> => {
      try {
        setSaveStatus('saving');
        const newRel = await createRelationship(caseId, data);
        setRelationships((prev) => [...prev, newRel]);
        setSaveStatus('saved');
        setTimeout(() => setSaveStatus('idle'), 2000);
        return newRel;
      } catch (err) {
        setError(err instanceof Error ? err.message : '관계 추가에 실패했습니다.');
        setSaveStatus('error');
        return null;
      }
    },
    [caseId]
  );

  // Update relationship
  const updateRelationshipData = useCallback(
    async (
      relationshipId: string,
      data: RelationshipUpdate
    ): Promise<PartyRelationship | null> => {
      try {
        setSaveStatus('saving');
        const updated = await updateRelationship(caseId, relationshipId, data);
        setRelationships((prev) =>
          prev.map((rel) => (rel.id === relationshipId ? updated : rel))
        );
        setSaveStatus('saved');
        setTimeout(() => setSaveStatus('idle'), 2000);
        return updated;
      } catch (err) {
        setError(err instanceof Error ? err.message : '관계 수정에 실패했습니다.');
        setSaveStatus('error');
        return null;
      }
    },
    [caseId]
  );

  // Delete relationship
  const deleteRelationshipById = useCallback(
    async (relationshipId: string): Promise<boolean> => {
      try {
        setSaveStatus('saving');
        await deleteRelationship(caseId, relationshipId);
        setRelationships((prev) =>
          prev.filter((rel) => rel.id !== relationshipId)
        );
        setSaveStatus('saved');
        setTimeout(() => setSaveStatus('idle'), 2000);
        return true;
      } catch (err) {
        setError(err instanceof Error ? err.message : '관계 삭제에 실패했습니다.');
        setSaveStatus('error');
        return false;
      }
    },
    [caseId]
  );

  return {
    nodes,
    relationships,
    isLoading,
    error,
    saveStatus,
    addNode,
    updateNode,
    deleteNode,
    addRelationship,
    updateRelationshipData,
    deleteRelationshipById,
    updateNodePosition,
    refresh: fetchGraph,
  };
}

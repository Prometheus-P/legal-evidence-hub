/**
 * useSpeakerMapping hook for 015-evidence-speaker-mapping
 * Manages speaker mapping state and validation
 */

'use client';

import { useState, useCallback, useMemo } from 'react';
import type { PartyNode } from '@/types/party';
import type {
  SpeakerMapping,
  SpeakerMappingItem,
  SpeakerMappingUpdateRequest,
  SpeakerMappingUpdateResponse,
} from '@/types/evidence';

// Validation constants
const MAX_SPEAKERS = 10;
const MAX_LABEL_LENGTH = 50;

export type SpeakerMappingSaveStatus = 'idle' | 'saving' | 'saved' | 'error';

interface UseSpeakerMappingOptions {
  /** Initial speaker mapping from evidence */
  initialMapping?: SpeakerMapping;
  /** Available parties from the case */
  parties: PartyNode[];
  /** Callback when mapping is saved successfully */
  onSaveSuccess?: (response: SpeakerMappingUpdateResponse) => void;
  /** Callback when save fails */
  onSaveError?: (error: Error) => void;
}

interface UseSpeakerMappingReturn {
  // State
  mapping: SpeakerMapping;
  isDirty: boolean;
  saveStatus: SpeakerMappingSaveStatus;
  validationErrors: string[];

  // Actions
  setMappingItem: (speakerLabel: string, partyId: string, partyName: string) => void;
  removeMappingItem: (speakerLabel: string) => void;
  clearMapping: () => void;
  resetMapping: () => void;

  // Save
  save: (
    saveFn: (request: SpeakerMappingUpdateRequest) => Promise<SpeakerMappingUpdateResponse>
  ) => Promise<boolean>;

  // Helpers
  getPartyById: (partyId: string) => PartyNode | undefined;
  getUnmappedSpeakers: (speakerLabels: string[]) => string[];
  isValid: boolean;
}

/**
 * Hook for managing speaker mapping in evidence detail view
 */
export function useSpeakerMapping({
  initialMapping = {},
  parties,
  onSaveSuccess,
  onSaveError,
}: UseSpeakerMappingOptions): UseSpeakerMappingReturn {
  const [mapping, setMapping] = useState<SpeakerMapping>(initialMapping);
  const [saveStatus, setSaveStatus] = useState<SpeakerMappingSaveStatus>('idle');

  // Check if mapping has changed from initial
  const isDirty = useMemo(() => {
    const initialKeys = Object.keys(initialMapping);
    const currentKeys = Object.keys(mapping);

    if (initialKeys.length !== currentKeys.length) return true;

    return currentKeys.some((key) => {
      const initial = initialMapping[key];
      const current = mapping[key];
      if (!initial || !current) return true;
      return initial.party_id !== current.party_id;
    });
  }, [initialMapping, mapping]);

  // Validation
  const validationErrors = useMemo(() => {
    const errors: string[] = [];

    if (Object.keys(mapping).length > MAX_SPEAKERS) {
      errors.push(`화자는 최대 ${MAX_SPEAKERS}명까지 매핑할 수 있습니다`);
    }

    for (const [label, item] of Object.entries(mapping)) {
      if (label.length > MAX_LABEL_LENGTH) {
        errors.push(`화자명 "${label}"이 너무 깁니다 (최대 ${MAX_LABEL_LENGTH}자)`);
      }
      if (!item.party_id) {
        errors.push(`"${label}"에 인물을 선택해주세요`);
      }
      // Verify party exists in case
      const partyExists = parties.some((p) => p.id === item.party_id);
      if (item.party_id && !partyExists) {
        errors.push(`"${label}"에 매핑된 인물이 존재하지 않습니다`);
      }
    }

    return errors;
  }, [mapping, parties]);

  const isValid = validationErrors.length === 0;

  // Set a single mapping item
  const setMappingItem = useCallback(
    (speakerLabel: string, partyId: string, partyName: string) => {
      setMapping((prev) => ({
        ...prev,
        [speakerLabel]: {
          party_id: partyId,
          party_name: partyName,
        } as SpeakerMappingItem,
      }));
    },
    []
  );

  // Remove a single mapping item
  const removeMappingItem = useCallback((speakerLabel: string) => {
    setMapping((prev) => {
      const next = { ...prev };
      delete next[speakerLabel];
      return next;
    });
  }, []);

  // Clear all mappings
  const clearMapping = useCallback(() => {
    setMapping({});
  }, []);

  // Reset to initial mapping
  const resetMapping = useCallback(() => {
    setMapping(initialMapping);
  }, [initialMapping]);

  // Save mapping via provided save function
  const save = useCallback(
    async (
      saveFn: (request: SpeakerMappingUpdateRequest) => Promise<SpeakerMappingUpdateResponse>
    ): Promise<boolean> => {
      if (!isValid) {
        return false;
      }

      setSaveStatus('saving');

      try {
        const request: SpeakerMappingUpdateRequest = {
          speaker_mapping: mapping,
        };
        const response = await saveFn(request);
        setSaveStatus('saved');

        // Reset to idle after delay
        setTimeout(() => setSaveStatus('idle'), 2000);

        onSaveSuccess?.(response);
        return true;
      } catch (err) {
        setSaveStatus('error');
        onSaveError?.(err instanceof Error ? err : new Error('저장에 실패했습니다'));
        return false;
      }
    },
    [mapping, isValid, onSaveSuccess, onSaveError]
  );

  // Helper: get party by ID
  const getPartyById = useCallback(
    (partyId: string): PartyNode | undefined => {
      return parties.find((p) => p.id === partyId);
    },
    [parties]
  );

  // Helper: get speakers that are not yet mapped
  const getUnmappedSpeakers = useCallback(
    (speakerLabels: string[]): string[] => {
      return speakerLabels.filter((label) => !mapping[label]);
    },
    [mapping]
  );

  return {
    mapping,
    isDirty,
    saveStatus,
    validationErrors,
    setMappingItem,
    removeMappingItem,
    clearMapping,
    resetMapping,
    save,
    getPartyById,
    getUnmappedSpeakers,
    isValid,
  };
}

/**
 * Extract unique speaker labels from evidence content
 * Detects common patterns like "나:", "상대방:", "홍길동:" etc.
 */
export function extractSpeakersFromContent(content: string): string[] {
  if (!content) return [];

  // Pattern to match speaker labels at start of lines
  // Matches: "이름:", "이름 :", "[이름]", etc.
  const patterns = [
    /^([가-힣a-zA-Z0-9_]+)\s*:/gm, // "이름:"
    /^\[([가-힣a-zA-Z0-9_]+)\]/gm, // "[이름]"
  ];

  const speakers = new Set<string>();

  for (const pattern of patterns) {
    let match;
    while ((match = pattern.exec(content)) !== null) {
      const speaker = match[1].trim();
      if (speaker && speaker.length <= MAX_LABEL_LENGTH) {
        speakers.add(speaker);
      }
    }
  }

  // Common chat speakers
  const commonSpeakers = ['나', '상대방', '본인', '배우자'];
  for (const speaker of commonSpeakers) {
    if (content.includes(`${speaker}:`) || content.includes(`${speaker} :`)) {
      speakers.add(speaker);
    }
  }

  return Array.from(speakers).sort();
}

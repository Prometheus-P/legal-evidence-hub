/**
 * useEvidenceLinks hook for LEH Lawyer Portal v1
 * User Story 4: Evidence-Party Linking
 */

'use client';

import { useState, useCallback, useEffect } from 'react';
import type { EvidencePartyLink, EvidenceLinkCreate } from '@/types/party';
import {
  getEvidenceLinks,
  getLinksForEvidence,
  getLinksForParty,
  createEvidenceLink,
  deleteEvidenceLink,
} from '@/lib/api/evidence-links';

interface UseEvidenceLinksOptions {
  caseId: string;
  evidenceId?: string;
  partyId?: string;
}

interface UseEvidenceLinksReturn {
  links: EvidencePartyLink[];
  isLoading: boolean;
  error: string | null;
  addLink: (data: EvidenceLinkCreate) => Promise<EvidencePartyLink | null>;
  removeLink: (linkId: string) => Promise<boolean>;
  refresh: () => Promise<void>;
}

export function useEvidenceLinks({
  caseId,
  evidenceId,
  partyId,
}: UseEvidenceLinksOptions): UseEvidenceLinksReturn {
  const [links, setLinks] = useState<EvidencePartyLink[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchLinks = useCallback(async () => {
    if (!caseId) return;

    setIsLoading(true);
    setError(null);

    try {
      let fetchedLinks: EvidencePartyLink[];

      if (evidenceId) {
        fetchedLinks = await getLinksForEvidence(caseId, evidenceId);
      } else if (partyId) {
        fetchedLinks = await getLinksForParty(caseId, partyId);
      } else {
        fetchedLinks = await getEvidenceLinks(caseId);
      }

      setLinks(fetchedLinks);
    } catch (err) {
      setError(err instanceof Error ? err.message : '연결 목록을 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  }, [caseId, evidenceId, partyId]);

  useEffect(() => {
    fetchLinks();
  }, [fetchLinks]);

  const addLink = useCallback(
    async (data: EvidenceLinkCreate): Promise<EvidencePartyLink | null> => {
      try {
        const newLink = await createEvidenceLink(caseId, data);
        setLinks((prev) => [...prev, newLink]);
        return newLink;
      } catch (err) {
        setError(err instanceof Error ? err.message : '연결 추가에 실패했습니다.');
        return null;
      }
    },
    [caseId]
  );

  const removeLink = useCallback(
    async (linkId: string): Promise<boolean> => {
      try {
        await deleteEvidenceLink(caseId, linkId);
        setLinks((prev) => prev.filter((link) => link.id !== linkId));
        return true;
      } catch (err) {
        setError(err instanceof Error ? err.message : '연결 삭제에 실패했습니다.');
        return false;
      }
    },
    [caseId]
  );

  return {
    links,
    isLoading,
    error,
    addLink,
    removeLink,
    refresh: fetchLinks,
  };
}

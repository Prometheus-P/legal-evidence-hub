/**
 * EvidenceLinkPopover - Popover showing evidence linked to a party
 * User Story 4: Evidence-Party Linking
 */

'use client';

import { useState } from 'react';
import type { EvidencePartyLink, PartyNode, LinkType } from '@/types/party';
import { LINK_TYPE_LABELS } from '@/types/party';

interface EvidenceLinkPopoverProps {
  party: PartyNode;
  links: EvidencePartyLink[];
  isLoading: boolean;
  onClose: () => void;
  onLinkEvidence: () => void;
  onRemoveLink: (linkId: string) => Promise<void>;
  onViewEvidence: (evidenceId: string) => void;
}

// Badge colors for link types
const LINK_TYPE_COLORS: Record<LinkType, string> = {
  mentions: 'bg-blue-100 text-blue-700',
  proves: 'bg-green-100 text-green-700',
  involves: 'bg-yellow-100 text-yellow-700',
  contradicts: 'bg-red-100 text-red-700',
};

export function EvidenceLinkPopover({
  party,
  links,
  isLoading,
  onClose,
  onLinkEvidence,
  onRemoveLink,
  onViewEvidence,
}: EvidenceLinkPopoverProps) {
  const [removingId, setRemovingId] = useState<string | null>(null);

  const handleRemove = async (linkId: string) => {
    setRemovingId(linkId);
    try {
      await onRemoveLink(linkId);
    } finally {
      setRemovingId(null);
    }
  };

  return (
    <div className="absolute z-50 w-80 bg-white rounded-lg shadow-xl border">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b">
        <div>
          <h3 className="font-medium text-gray-900">{party.name}</h3>
          <p className="text-xs text-gray-500">연결된 증거</p>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Content */}
      <div className="max-h-64 overflow-y-auto">
        {isLoading ? (
          <div className="p-4 text-center text-gray-500">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto mb-2" />
            불러오는 중...
          </div>
        ) : links.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <p className="mb-2">연결된 증거가 없습니다</p>
          </div>
        ) : (
          <ul className="divide-y">
            {links.map((link) => (
              <li
                key={link.id}
                className="px-4 py-3 hover:bg-gray-50 flex items-start gap-3"
              >
                <div className="flex-1 min-w-0">
                  <button
                    onClick={() => onViewEvidence(link.evidence_id)}
                    className="text-sm font-medium text-blue-600 hover:underline truncate block w-full text-left"
                  >
                    증거 #{link.evidence_id.slice(0, 8)}
                  </button>
                  <span className={`inline-block mt-1 px-2 py-0.5 text-xs rounded-full ${LINK_TYPE_COLORS[link.link_type]}`}>
                    {LINK_TYPE_LABELS[link.link_type]}
                  </span>
                </div>
                <button
                  onClick={() => handleRemove(link.id)}
                  disabled={removingId === link.id}
                  className="text-gray-400 hover:text-red-500 disabled:opacity-50"
                  title="연결 해제"
                >
                  {removingId === link.id ? (
                    <div className="w-4 h-4 animate-spin rounded-full border-2 border-gray-300 border-t-gray-600" />
                  ) : (
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  )}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-3 border-t bg-gray-50 rounded-b-lg">
        <button
          onClick={onLinkEvidence}
          className="w-full px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
        >
          + 증거 연결하기
        </button>
      </div>
    </div>
  );
}

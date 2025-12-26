/**
 * DraftSplitView Component
 *
 * A split view layout for drafting documents with a reference panel.
 * Combines DraftPreviewPanel with evidence, LSSP keypoints, or precedent references.
 *
 * Part of Phase B.2 (polymorphic-dazzling-oasis.md) implementation.
 */

'use client';

import React, { useState, useCallback } from 'react';
import {
  PanelRightClose,
  PanelRightOpen,
  FileText,
  Tag,
  Scale,
  X,
} from 'lucide-react';
import DraftPreviewPanel from './DraftPreviewPanel';
import { EvidenceReferenceList } from './EvidenceReferenceList';
import { LSSPKeypointReferenceList } from './LSSPKeypointReferenceList';
import { PrecedentReferenceList } from './PrecedentReferenceList';
import { Evidence } from '@/types/evidence';
import { Keypoint } from '@/lib/api/lssp';
import { DraftCitation, PrecedentCitation } from '@/types/draft';

// =============================================================================
// Types
// =============================================================================

export type ReferenceTabType = 'evidence' | 'keypoints' | 'precedents';

export interface DraftSplitViewProps {
  /**
   * Case ID for the draft
   */
  caseId: string;

  /**
   * Draft text content
   */
  draftText: string;

  /**
   * Evidence citations in the draft
   */
  citations: DraftCitation[];

  /**
   * Precedent citations (optional)
   */
  precedentCitations?: PrecedentCitation[];

  /**
   * Whether draft is being generated
   */
  isGenerating: boolean;

  /**
   * Whether there's an existing draft
   */
  hasExistingDraft: boolean;

  /**
   * Handler for generating draft
   */
  onGenerate: () => void;

  /**
   * Handler for manual save
   */
  onManualSave?: (content: string) => Promise<void> | void;

  /**
   * Evidence items for reference panel
   */
  evidenceItems?: Evidence[];

  /**
   * Keypoints for reference panel
   */
  keypoints?: Keypoint[];

  /**
   * Whether evidence is loading
   */
  isEvidenceLoading?: boolean;

  /**
   * Whether keypoints are loading
   */
  isKeypointsLoading?: boolean;

  /**
   * Handler when user inserts an evidence citation
   */
  onInsertEvidenceCitation?: (evidenceId: string, quote?: string) => void;

  /**
   * Handler when user views evidence details
   */
  onViewEvidence?: (evidenceId: string) => void;

  /**
   * Handler when user inserts a keypoint citation
   */
  onInsertKeypointCitation?: (keypointId: string, content: string) => void;

  /**
   * Handler when user inserts a precedent citation
   */
  onInsertPrecedentCitation?: (caseRef: string, summary: string) => void;

  /**
   * Initial reference panel state
   */
  defaultReferenceOpen?: boolean;

  /**
   * Initial reference tab
   */
  defaultReferenceTab?: ReferenceTabType;

  /**
   * Additional CSS classes
   */
  className?: string;
}

interface TabConfig {
  id: ReferenceTabType;
  label: string;
  icon: React.ReactNode;
  count?: number;
}

// =============================================================================
// Component
// =============================================================================

export function DraftSplitView({
  caseId,
  draftText,
  citations,
  precedentCitations = [],
  isGenerating,
  hasExistingDraft,
  onGenerate,
  onManualSave,
  evidenceItems = [],
  keypoints = [],
  isEvidenceLoading = false,
  isKeypointsLoading = false,
  onInsertEvidenceCitation,
  onViewEvidence,
  onInsertKeypointCitation,
  onInsertPrecedentCitation,
  defaultReferenceOpen = false,
  defaultReferenceTab = 'evidence',
  className = '',
}: DraftSplitViewProps) {
  const [isReferenceOpen, setIsReferenceOpen] = useState(defaultReferenceOpen);
  const [activeTab, setActiveTab] = useState<ReferenceTabType>(defaultReferenceTab);

  const handleToggleReference = useCallback(() => {
    setIsReferenceOpen((prev) => !prev);
  }, []);

  const handleCloseReference = useCallback(() => {
    setIsReferenceOpen(false);
  }, []);

  const handleInsertEvidence = useCallback(
    (evidenceId: string, quote?: string) => {
      if (onInsertEvidenceCitation) {
        onInsertEvidenceCitation(evidenceId, quote);
      }
    },
    [onInsertEvidenceCitation]
  );

  const handleInsertKeypoint = useCallback(
    (keypointId: string, content: string) => {
      if (onInsertKeypointCitation) {
        onInsertKeypointCitation(keypointId, content);
      }
    },
    [onInsertKeypointCitation]
  );

  const handleInsertPrecedent = useCallback(
    (caseRef: string, summary: string) => {
      if (onInsertPrecedentCitation) {
        onInsertPrecedentCitation(caseRef, summary);
      }
    },
    [onInsertPrecedentCitation]
  );

  // Tab configurations
  const tabs: TabConfig[] = [
    {
      id: 'evidence',
      label: '증거',
      icon: <FileText className="w-4 h-4" />,
      count: evidenceItems.length,
    },
    {
      id: 'keypoints',
      label: '쟁점',
      icon: <Tag className="w-4 h-4" />,
      count: keypoints.length,
    },
    {
      id: 'precedents',
      label: '판례',
      icon: <Scale className="w-4 h-4" />,
      count: precedentCitations.length,
    },
  ];

  return (
    <div className={`flex h-full ${className}`}>
      {/* Left: Draft Editor */}
      <div
        className={`flex-1 min-w-0 transition-all duration-300 ${
          isReferenceOpen ? 'pr-0' : ''
        }`}
      >
        <div className="relative h-full">
          {/* Toggle Reference Panel Button */}
          <button
            type="button"
            onClick={handleToggleReference}
            className="absolute top-4 right-4 z-10 p-2 bg-white dark:bg-neutral-800 border border-gray-200 dark:border-neutral-700 rounded-lg shadow-sm hover:bg-gray-50 dark:hover:bg-neutral-700 transition-colors"
            title={isReferenceOpen ? '참고 패널 닫기' : '참고 패널 열기'}
          >
            {isReferenceOpen ? (
              <PanelRightClose className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            ) : (
              <PanelRightOpen className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            )}
          </button>

          <DraftPreviewPanel
            caseId={caseId}
            draftText={draftText}
            citations={citations}
            precedentCitations={precedentCitations}
            isGenerating={isGenerating}
            hasExistingDraft={hasExistingDraft}
            onGenerate={onGenerate}
            onManualSave={onManualSave}
          />
        </div>
      </div>

      {/* Right: Reference Panel */}
      {isReferenceOpen && (
        <div className="w-80 lg:w-96 flex-shrink-0 border-l border-gray-200 dark:border-neutral-700 bg-gray-50 dark:bg-neutral-900 flex flex-col overflow-hidden">
          {/* Reference Panel Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-neutral-700 bg-white dark:bg-neutral-800">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
              참고 자료
            </h3>
            <button
              type="button"
              onClick={handleCloseReference}
              className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-neutral-700 rounded transition-colors"
              title="닫기"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Reference Tabs */}
          <div className="flex border-b border-gray-200 dark:border-neutral-700 bg-white dark:bg-neutral-800">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-2.5 text-xs font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400 bg-blue-50/50 dark:bg-blue-900/20'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-50 dark:hover:bg-neutral-700'
                }`}
              >
                {tab.icon}
                <span>{tab.label}</span>
                {tab.count !== undefined && tab.count > 0 && (
                  <span
                    className={`px-1.5 py-0.5 text-xs rounded-full ${
                      activeTab === tab.id
                        ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300'
                        : 'bg-gray-100 dark:bg-neutral-700 text-gray-600 dark:text-gray-400'
                    }`}
                  >
                    {tab.count}
                  </span>
                )}
              </button>
            ))}
          </div>

          {/* Reference Content */}
          <div className="flex-1 overflow-y-auto">
            {activeTab === 'evidence' && (
              <EvidenceReferenceList
                items={evidenceItems}
                onInsertCitation={handleInsertEvidence}
                onViewEvidence={onViewEvidence}
                isLoading={isEvidenceLoading}
              />
            )}

            {activeTab === 'keypoints' && (
              <LSSPKeypointReferenceList
                keypoints={keypoints}
                onInsertCitation={handleInsertKeypoint}
                isLoading={isKeypointsLoading}
              />
            )}

            {activeTab === 'precedents' && (
              <PrecedentReferenceList
                precedents={precedentCitations}
                onInsertCitation={handleInsertPrecedent}
                isLoading={false}
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default DraftSplitView;

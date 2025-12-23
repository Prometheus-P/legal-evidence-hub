'use client';

/**
 * DataPanel - Left Panel Accordion Component
 * 014-ui-settings-completion Feature
 *
 * Collapsible accordion lists for:
 * - Evidence (with legal numbering: 갑제1호증, 을제1호증)
 * - Consultation history
 * - Assets
 */

import { useState, ReactNode } from 'react';
import { ChevronDown, ChevronRight, FileText, MessageSquare, Wallet, Plus, Upload } from 'lucide-react';

interface AccordionSection {
  id: string;
  title: string;
  icon: ReactNode;
  count?: number;
  content: ReactNode;
  action?: {
    label: string;
    icon: ReactNode;
    onClick: () => void;
  };
}

interface DataPanelProps {
  sections: AccordionSection[];
  defaultOpenSections?: string[];
}

export function DataPanel({ sections, defaultOpenSections = ['evidence'] }: DataPanelProps) {
  const [openSections, setOpenSections] = useState<Set<string>>(new Set(defaultOpenSections));

  const toggleSection = (sectionId: string) => {
    setOpenSections((prev) => {
      const next = new Set(prev);
      if (next.has(sectionId)) {
        next.delete(sectionId);
      } else {
        next.add(sectionId);
      }
      return next;
    });
  };

  return (
    <div className="divide-y divide-gray-200 dark:divide-neutral-700">
      {sections.map((section) => {
        const isOpen = openSections.has(section.id);

        return (
          <div key={section.id}>
            {/* Section Header */}
            <button
              onClick={() => toggleSection(section.id)}
              className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-50 dark:hover:bg-neutral-750 transition-colors"
            >
              <div className="flex items-center gap-2">
                <span className="text-[var(--color-text-secondary)]">
                  {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                </span>
                <span className="text-[var(--color-text-secondary)]">{section.icon}</span>
                <span className="text-sm font-medium text-[var(--color-text-primary)]">
                  {section.title}
                </span>
                {section.count !== undefined && section.count > 0 && (
                  <span className="ml-1 px-1.5 py-0.5 text-xs bg-gray-100 dark:bg-neutral-700 text-[var(--color-text-secondary)] rounded">
                    {section.count}
                  </span>
                )}
              </div>
              {section.action && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    section.action?.onClick();
                  }}
                  className="p-1 rounded hover:bg-gray-200 dark:hover:bg-neutral-600 text-[var(--color-primary)]"
                  aria-label={section.action.label}
                >
                  {section.action.icon}
                </button>
              )}
            </button>

            {/* Section Content */}
            {isOpen && (
              <div className="px-4 pb-3">
                {section.content}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

// Convenience wrapper for case detail page
interface CaseDataPanelProps {
  evidenceContent: ReactNode;
  evidenceCount: number;
  onUploadEvidence: () => void;
  consultationContent: ReactNode;
  consultationCount?: number;
  onAddConsultation: () => void;
  assetsContent: ReactNode;
  assetsCount?: number;
  onAddAsset: () => void;
}

export function CaseDataPanel({
  evidenceContent,
  evidenceCount,
  onUploadEvidence,
  consultationContent,
  consultationCount = 0,
  onAddConsultation,
  assetsContent,
  assetsCount = 0,
  onAddAsset,
}: CaseDataPanelProps) {
  const sections: AccordionSection[] = [
    {
      id: 'evidence',
      title: '증거 목록',
      icon: <FileText className="w-4 h-4" />,
      count: evidenceCount,
      content: evidenceContent,
      action: {
        label: '증거 업로드',
        icon: <Upload className="w-4 h-4" />,
        onClick: onUploadEvidence,
      },
    },
    {
      id: 'consultation',
      title: '상담 내역',
      icon: <MessageSquare className="w-4 h-4" />,
      count: consultationCount,
      content: consultationContent,
      action: {
        label: '상담 추가',
        icon: <Plus className="w-4 h-4" />,
        onClick: onAddConsultation,
      },
    },
    {
      id: 'assets',
      title: '재산 목록',
      icon: <Wallet className="w-4 h-4" />,
      count: assetsCount,
      content: assetsContent,
      action: {
        label: '재산 추가',
        icon: <Plus className="w-4 h-4" />,
        onClick: onAddAsset,
      },
    },
  ];

  return <DataPanel sections={sections} defaultOpenSections={['evidence']} />;
}

export default DataPanel;

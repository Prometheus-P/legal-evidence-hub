/**
 * Case Relations Page
 * 009-calm-control-design-system
 *
 * Displays the party relations graph for a case using React Flow.
 */

import CaseRelationsClient from './CaseRelationsClient';

// Static params for build-time generation
// Includes E2E test IDs (test-case-001, test-case-empty)
export function generateStaticParams() {
  return [
    { id: '1' },
    { id: '2' },
    { id: '3' },
    { id: 'test-case-001' },
    { id: 'test-case-empty' },
  ];
}

// Allow dynamic routes not listed in generateStaticParams
export const dynamicParams = true;

interface Props {
  params: Promise<{ id: string }>;
}

export default async function CaseRelationsPage({ params }: Props) {
  const { id } = await params;

  return <CaseRelationsClient caseId={id} />;
}

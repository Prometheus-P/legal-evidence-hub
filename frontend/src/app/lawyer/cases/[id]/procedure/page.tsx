/**
 * Procedure Page (Server Component wrapper)
 * T145 - US3: Procedure stage tracking page for a case
 */

import ProcedureClient from './ProcedureClient';

// Required for static export with dynamic routes
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

interface PageProps {
  params: { id: string };
}

export default function ProcedurePage({ params }: PageProps) {
  return <ProcedureClient caseId={params.id} />;
}

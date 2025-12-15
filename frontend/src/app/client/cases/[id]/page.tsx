/**
 * Client Case Detail Page
 * 003-role-based-ui Feature - US4 (T075)
 *
 * Server component wrapper with static export support.
 */

import ClientCaseDetailClient from './ClientCaseDetailClient';

// Allow dynamic routes not listed in generateStaticParams
export const dynamicParams = true;

// Pre-render placeholder routes for static export
export function generateStaticParams() {
  return [{ id: '1' }, { id: '2' }, { id: '3' }];
}

interface PageProps {
  params: { id: string };
}

export default function ClientCaseDetailPage({ params }: PageProps) {
  return <ClientCaseDetailClient caseId={params.id} />;
}

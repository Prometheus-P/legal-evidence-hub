/**
 * Detective Investigation Detail Page
 * 003-role-based-ui Feature - US5 (T103)
 *
 * Server component wrapper with static export support.
 */

import DetectiveCaseDetailClient from './DetectiveCaseDetailClient';

// Allow dynamic routes not listed in generateStaticParams
export const dynamicParams = true;

// Pre-render placeholder routes for static export
export function generateStaticParams() {
  return [{ id: '1' }, { id: '2' }, { id: '3' }];
}

interface PageProps {
  params: { id: string };
}

export default function DetectiveCaseDetailPage({ params }: PageProps) {
  return <DetectiveCaseDetailClient caseId={params.id} />;
}

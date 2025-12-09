/**
 * Case Relations Page
 * 009-calm-control-design-system
 *
 * Displays the party relations graph for a case using React Flow.
 */

import CaseRelationsClient from './CaseRelationsClient';

// Static params for build-time generation
export function generateStaticParams() {
  return [{ id: '1' }, { id: '2' }, { id: '3' }];
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

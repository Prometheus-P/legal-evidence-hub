/**
 * Case Assets Page
 * 009-calm-control-design-system
 *
 * Asset division management for divorce cases.
 */

import CaseAssetsClient from './CaseAssetsClient';

// Static params for build-time generation
export function generateStaticParams() {
  return [{ id: '1' }, { id: '2' }, { id: '3' }];
}

// Allow dynamic routes not listed in generateStaticParams
export const dynamicParams = true;

interface Props {
  params: Promise<{ id: string }>;
}

export default async function CaseAssetsPage({ params }: Props) {
  const { id } = await params;

  return <CaseAssetsClient caseId={id} />;
}

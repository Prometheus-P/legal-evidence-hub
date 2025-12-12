import LawyerCaseDetailClient from './LawyerCaseDetailClient';

// Required for static export with dynamic routes
// Pre-render sample case pages; additional routes are handled at request time
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

export default function LawyerCaseDetailPage({ params }: PageProps) {
  return <LawyerCaseDetailClient id={params.id} />;
}

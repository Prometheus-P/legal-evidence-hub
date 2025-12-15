import CaseDetailClient from '@/components/case/CaseDetailClient';

// Allow dynamic routes not listed in generateStaticParams
export const dynamicParams = true;

// Pre-render placeholder routes for static export
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

interface PageProps {
  params: { id: string };
}

export default function LawyerCaseDetailPage({ params }: PageProps) {
  return (
    <CaseDetailClient
      id={params.id}
      apiBasePath="/lawyer"
      defaultReturnUrl="/lawyer/cases"
    />
  );
}

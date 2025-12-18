/**
 * Hook to extract case ID from URL for static export fallback support.
 *
 * When Next.js static export is served via CloudFront/S3:
 * - Dynamic routes not in generateStaticParams get served with fallback HTML
 * - We use query parameters (?caseId=xxx) instead of path segments
 *
 * This hook extracts the case ID from query params or URL path.
 *
 * @param fallbackId - The ID passed from page params (build-time value or explicit prop)
 * @returns The effective case ID (query param > URL path > fallback)
 */

'use client';

import { usePathname, useSearchParams } from 'next/navigation';

/**
 * Extract case ID from URL path (legacy support).
 * Matches patterns like:
 * - /lawyer/cases/{id}/
 * - /client/cases/{id}/
 * - /detective/cases/{id}/
 */
function extractCaseIdFromPath(pathname: string): string | null {
  // Match /{role}/cases/{id} where id is NOT a known section
  const match = pathname.match(/^\/(lawyer|client|detective|staff)\/cases\/([^/]+)/);
  if (!match) return null;

  const potentialId = match[2];
  // Known section names - not case IDs
  const sections = ['detail', 'procedure', 'assets', 'relations', 'relationship'];
  if (sections.includes(potentialId)) {
    return null;
  }

  return potentialId;
}

/**
 * Hook to get the effective case ID.
 * Priority: query param (caseId) > URL path segment > fallback prop
 *
 * @param fallbackId - The ID from page params or explicit prop
 * @returns The effective case ID
 *
 * @example
 * ```tsx
 * // In a client component receiving caseId from query param
 * function CaseDetailClient({ id }: { id: string }) {
 *   const caseId = useCaseIdFromUrl(id);
 *   // For /lawyer/cases/detail/?caseId=abc123, returns 'abc123'
 * }
 * ```
 */
export function useCaseIdFromUrl(fallbackId: string): string {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  // Priority 1: Query parameter (preferred for static export)
  const queryParamId = searchParams.get('caseId');
  if (queryParamId) {
    return queryParamId;
  }

  // Priority 2: URL path segment (legacy dynamic route support)
  const pathCaseId = extractCaseIdFromPath(pathname);
  if (pathCaseId) {
    return pathCaseId;
  }

  // Priority 3: Fallback from props
  return fallbackId;
}

export default useCaseIdFromUrl;

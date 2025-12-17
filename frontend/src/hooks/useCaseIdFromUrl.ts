/**
 * Hook to extract case ID from URL path for static export fallback support.
 *
 * When Next.js static export is served via CloudFront/S3, dynamic routes not
 * listed in generateStaticParams get served with a fallback HTML file.
 * The params.id from build time won't match the actual URL.
 *
 * This hook extracts the real case ID from the browser's URL path.
 *
 * @param fallbackId - The ID passed from page params (build-time value)
 * @returns The effective case ID (URL path preferred over fallback)
 */

'use client';

import { usePathname } from 'next/navigation';

/**
 * Extract case ID from URL path.
 * Matches patterns like:
 * - /lawyer/cases/{id}/
 * - /lawyer/cases/{id}/procedure/
 * - /client/cases/{id}/
 * - /detective/cases/{id}/
 */
function extractCaseIdFromPath(pathname: string): string | null {
  // Match /{role}/cases/{id} or /{role}/cases/{id}/{section}
  const match = pathname.match(/^\/(lawyer|client|detective|staff)\/cases\/([^/]+)/);
  return match ? match[2] : null;
}

/**
 * Hook to get the effective case ID, preferring URL path over build-time params.
 *
 * @param fallbackId - The ID from page params (may be incorrect for dynamic routes in static export)
 * @returns The effective case ID extracted from the current URL path
 *
 * @example
 * ```tsx
 * // In a client component
 * function CaseDetailClient({ id }: { id: string }) {
 *   const caseId = useCaseIdFromUrl(id);
 *   // caseId will be the actual ID from URL, not the build-time params.id
 * }
 * ```
 */
export function useCaseIdFromUrl(fallbackId: string): string {
  const pathname = usePathname();
  const urlCaseId = extractCaseIdFromPath(pathname);

  // Prefer URL path over build-time params
  // This handles CloudFront serving pre-rendered HTML for dynamic routes
  return urlCaseId || fallbackId;
}

export default useCaseIdFromUrl;

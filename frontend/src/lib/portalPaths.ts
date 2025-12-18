/**
 * Portal path helpers
 * Generates role-aware URLs for case detail pages.
 *
 * IMPORTANT: Uses query parameters for case detail pages to support
 * Next.js static export. Dynamic route segments (/{role}/cases/{caseId}/)
 * don't work in static export because those HTML files don't exist in S3.
 *
 * Solution: Use /{role}/cases/detail/?caseId=xxx which always exists.
 */

export type PortalRole = 'lawyer' | 'client' | 'detective';
export type CaseSection = 'detail' | 'procedure' | 'assets' | 'relations' | 'relationship';

interface CasePathOptions {
  returnUrl?: string;
  tab?: string;
  [key: string]: string | undefined;
}

/**
 * Build a query-parameter-based case URL for static export compatibility.
 * Format: /{role}/cases/{section}/?caseId={caseId}&...
 *
 * This ensures the URL always points to a pre-rendered HTML file.
 */
function buildCasePath(
  role: PortalRole,
  section: CaseSection,
  caseId: string,
  options: CasePathOptions = {}
): string {
  // Validate caseId to prevent invalid URLs
  if (!caseId || caseId === 'undefined' || caseId === 'null') {
    console.error('[portalPaths] Invalid caseId:', caseId);
    return `/${role}/cases/`;
  }

  // Build base path - always use static section paths
  let path = `/${role}/cases/${section}/`;

  // Build query params with caseId first
  const queryParams: string[] = [`caseId=${encodeURIComponent(caseId)}`];

  // Add optional query params
  Object.entries(options)
    .filter(([, value]) => value !== undefined && value !== null)
    .forEach(([key, value]) => {
      queryParams.push(`${encodeURIComponent(key)}=${encodeURIComponent(value!)}`);
    });

  path += `?${queryParams.join('&')}`;

  return path;
}

/**
 * Build a case detail path using query parameters.
 * Example: /lawyer/cases/detail/?caseId=case_abc123
 */
export function getCaseDetailPath(
  role: PortalRole,
  caseId: string,
  options: CasePathOptions = {}
): string {
  return buildCasePath(role, 'detail', caseId, options);
}

/**
 * Convenience helper for lawyer-only sub pages (procedure/assets/relations/etc.)
 * Example: /lawyer/cases/procedure/?caseId=case_abc123
 */
export function getLawyerCasePath(
  section: Exclude<CaseSection, 'detail'> | 'detail',
  caseId: string,
  options: CasePathOptions = {}
): string {
  return buildCasePath('lawyer', section, caseId, options);
}

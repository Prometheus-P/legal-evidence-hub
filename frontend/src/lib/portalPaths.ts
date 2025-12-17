/**
 * Portal path helpers
 * Generates role-aware URLs for case detail pages using path parameters.
 *
 * Uses dynamic routes: /{role}/cases/{caseId}/ instead of query params
 * to avoid S3 redirect issues that strip query parameters.
 */

export type PortalRole = 'lawyer' | 'client' | 'detective';
export type CaseSection = 'detail' | 'procedure' | 'assets' | 'relations' | 'relationship';

interface CasePathOptions {
  returnUrl?: string;
  tab?: string;
  [key: string]: string | undefined;
}

/**
 * Build a path-based case URL using dynamic route segments.
 * Format: /{role}/cases/{caseId}/{section?}/
 *
 * This avoids S3 302 redirects that strip query parameters.
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
    // Return cases list to trigger navigation to list page
    return `/${role}/cases/`;
  }

  // Build base path with caseId in path segment
  let path = `/${role}/cases/${caseId}`;

  // Add section if not 'detail' (detail is the default at /{role}/cases/{id}/)
  if (section !== 'detail') {
    path += `/${section}`;
  }

  // Always add trailing slash for S3 compatibility
  path += '/';

  // Add optional query params if provided (e.g., tab, returnUrl)
  const queryParams = Object.entries(options)
    .filter(([, value]) => value !== undefined && value !== null)
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value!)}`)
    .join('&');

  if (queryParams) {
    path += `?${queryParams}`;
  }

  return path;
}

/**
 * Build a case detail path using path parameters.
 * Example: /lawyer/cases/case_abc123/
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
 * Example: /lawyer/cases/case_abc123/procedure/
 */
export function getLawyerCasePath(
  section: Exclude<CaseSection, 'detail'> | 'detail',
  caseId: string,
  options: CasePathOptions = {}
): string {
  return buildCasePath('lawyer', section, caseId, options);
}

/**
 * Portal path helpers
 * Generates role-aware URLs for case detail pages that work with static hosting.
 */

export type PortalRole = 'lawyer' | 'client' | 'detective';
export type CaseSection = 'detail' | 'procedure' | 'assets' | 'relations' | 'relationship';

interface CasePathOptions {
  returnUrl?: string;
  tab?: string;
  [key: string]: string | undefined;
}

/**
 * Base paths for case pages using query parameters.
 * Static hosting (CloudFront + S3) requires pre-built pages,
 * so we use /cases/detail?caseId=xxx format instead of /cases/{id}
 */
const SECTION_BASE_PATH: Record<PortalRole, Partial<Record<CaseSection, string>>> = {
  lawyer: {
    detail: '/lawyer/cases/detail',
    procedure: '/lawyer/cases/procedure',
    assets: '/lawyer/cases/assets',
    relations: '/lawyer/cases/relations',
    relationship: '/lawyer/cases/relationship',
  },
  client: {
    detail: '/client/cases/detail',
  },
  detective: {
    detail: '/detective/cases/detail',
  },
};

function buildCasePath(
  role: PortalRole,
  section: CaseSection,
  caseId: string,
  options: CasePathOptions = {}
): string {
  const basePath =
    SECTION_BASE_PATH[role][section] ?? SECTION_BASE_PATH[role].detail ?? '/lawyer/cases/detail';

  // Validate caseId to prevent invalid URLs
  if (!caseId || caseId === 'undefined' || caseId === 'null') {
    console.error('[portalPaths] Invalid caseId:', caseId);
    // Return base path without query params to trigger the error state in detail page
    return basePath;
  }

  const params = new URLSearchParams();
  params.set('caseId', caseId);

  // Preserve optional params (e.g., tab, returnUrl, view mode)
  Object.entries(options).forEach(([key, value]) => {
    if (value) {
      params.set(key, value);
    }
  });

  // Add trailing slash before query params to prevent S3 301 redirect
  // which would strip query parameters (trailingSlash: true in next.config.js)
  return `${basePath}/?${params.toString()}`;
}

/**
 * Build a query-based case detail path for static hosting.
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
 */
export function getLawyerCasePath(
  section: Exclude<CaseSection, 'detail'> | 'detail',
  caseId: string,
  options: CasePathOptions = {}
): string {
  return buildCasePath('lawyer', section, caseId, options);
}

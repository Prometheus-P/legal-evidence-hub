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
 * Dynamic route patterns for case pages.
 * Uses /cases/{id} format instead of /cases/detail?caseId=xxx
 * to work properly with CloudFront static hosting.
 */
const SECTION_PATTERNS: Record<PortalRole, Partial<Record<CaseSection, string>>> = {
  lawyer: {
    detail: '/lawyer/cases/:id',
    procedure: '/lawyer/cases/:id/procedure',
    assets: '/lawyer/cases/:id/assets',
    relations: '/lawyer/cases/:id/relations',
    relationship: '/lawyer/cases/:id/relationship',
  },
  client: {
    detail: '/client/cases/:id',
  },
  detective: {
    detail: '/detective/cases/:id',
  },
};

function buildCasePath(
  role: PortalRole,
  section: CaseSection,
  caseId: string,
  options: CasePathOptions = {}
): string {
  const pattern =
    SECTION_PATTERNS[role][section] ?? SECTION_PATTERNS[role].detail ?? '/lawyer/cases/:id';

  // Validate caseId to prevent invalid URLs
  if (!caseId || caseId === 'undefined' || caseId === 'null') {
    console.error('[portalPaths] Invalid caseId:', caseId);
    // Return fallback path
    return `/${role}/cases`;
  }

  // Replace :id placeholder with actual caseId
  const basePath = pattern.replace(':id', caseId);

  // Build query string for optional params (tab, returnUrl, etc.)
  const params = new URLSearchParams();
  Object.entries(options).forEach(([key, value]) => {
    if (value) {
      params.set(key, value);
    }
  });

  const query = params.toString();
  return query ? `${basePath}?${query}` : basePath;
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

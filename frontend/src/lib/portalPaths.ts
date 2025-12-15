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
  const params = new URLSearchParams();
  params.set('caseId', caseId);

  // Preserve optional params (e.g., tab, returnUrl, view mode)
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

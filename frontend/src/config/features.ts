/**
 * Feature flags for LEH Lawyer Portal v1
 *
 * Toggle features on/off during development and gradual rollout.
 * Set to `true` when feature is ready for production.
 */

export const FEATURES = {
  // Phase 3: US1 - Party Relationship Graph (P1 MVP)
  // Backend: ✅ Complete | Frontend: ✅ Complete
  PARTY_GRAPH: true,

  // Phase 4: US4 - Evidence-Party Linking (P1 MVP)
  // Backend: ✅ Complete | Frontend: ✅ Complete
  EVIDENCE_PARTY_LINKS: true,

  // Phase 5: US5 - Dark Mode Toggle (P2 Amenities)
  // ✅ Complete - Theme provider with system preference detection
  DARK_MODE: true,

  // Phase 6: US6 - Global Search / Command Palette (P2 Amenities)
  // ✅ Complete - Cmd+K palette with fuzzy search
  GLOBAL_SEARCH: true,

  // Phase 7: US7 - Today View Dashboard (P2 Amenities)
  // ✅ Complete - Today's deadlines, hearings, tasks
  TODAY_VIEW: true,

  // Phase 8: US2 - Asset Sheet / Property Division (P2 Optional)
  // ✅ Complete - Asset management with division calculator
  ASSET_SHEET: true,

  // Phase 9: US3 - Procedure Stage Tracking (P2 Optional)
  // ✅ Complete - Stage timeline with completion tracking
  PROCEDURE_STAGES: true,

  // Phase 10: US8 - Summary Card Generation (P3)
  // ✅ Complete - Case summary cards with PDF export
  SUMMARY_CARD: true,
} as const;

export type FeatureKey = keyof typeof FEATURES;

/**
 * Check if a feature is enabled
 */
export function isFeatureEnabled(feature: FeatureKey): boolean {
  return FEATURES[feature];
}

/**
 * Feature guard component helper
 * Usage: {isFeatureEnabled('PARTY_GRAPH') && <PartyGraph />}
 */
export function withFeatureFlag<T>(
  feature: FeatureKey,
  enabledValue: T,
  disabledValue: T
): T {
  return isFeatureEnabled(feature) ? enabledValue : disabledValue;
}

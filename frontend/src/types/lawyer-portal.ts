/**
 * LEH Lawyer Portal v1 - Types Barrel Export
 *
 * Central export point for all lawyer portal related types.
 * Import from this file for cleaner imports:
 *   import { PartyNode, PartyGraphData } from '@/types/lawyer-portal';
 */

// Party Graph types (US1)
export * from './party';

// Re-export commonly used types for convenience
export type {
  PartyType,
  RelationshipType,
  LinkType,
  Position,
  PartyNode,
  PartyNodeCreate,
  PartyNodeUpdate,
  PartyRelationship,
  RelationshipCreate,
  RelationshipUpdate,
  PartyGraphData,
  EvidencePartyLink,
  EvidenceLinkCreate,
} from './party';

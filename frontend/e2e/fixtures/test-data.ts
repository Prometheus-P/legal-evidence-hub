/**
 * E2E Test Fixtures
 * Test data and constants for E2E tests
 */

// Test case ID for evidence processing tests
// Use a stable case ID from staging environment
export const TEST_CASE_ID = 'test-case-e2e';

// Test user credentials (for staging only)
export const TEST_USERS = {
  lawyer: {
    email: 'test-lawyer@example.com',
    password: 'test-password',
  },
  staff: {
    email: 'test-staff@example.com',
    password: 'test-password',
  },
};

// API endpoints
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://dpbf86zqulqfy.cloudfront.net/api';

// Mock person nodes (for relationship graph)
export const MOCK_PERSON_NODES = [
  {
    id: 'person-1',
    name: '원고',
    role: 'plaintiff',
    position: { x: 100, y: 100 }
  },
  {
    id: 'person-2',
    name: '피고',
    role: 'defendant',
    position: { x: 300, y: 100 }
  }
];

// Mock party nodes (for party graph)
export const MOCK_PARTY_NODES = [
  {
    id: 'party-1',
    name: '원고',
    party_type: 'plaintiff',
    position: { x: 100, y: 100 }
  },
  {
    id: 'party-2',
    name: '피고',
    party_type: 'defendant',
    position: { x: 300, y: 100 }
  }
];

// Mock party relationships
export const MOCK_PARTY_RELATIONSHIPS = [
  {
    id: 'rel-1',
    source_id: 'party-1',
    target_id: 'party-2',
    relationship_type: 'spouse',
    label: '배우자'
  }
];

// Mock relationship edges (for graph visualization)
export const MOCK_RELATIONSHIP_EDGES = [
  {
    id: 'edge-1',
    source: 'person-1',
    target: 'person-2',
    type: 'spouse',
    label: '배우자'
  }
];

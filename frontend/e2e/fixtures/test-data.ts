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

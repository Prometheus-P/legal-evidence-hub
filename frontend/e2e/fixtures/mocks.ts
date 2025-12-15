/**
 * Shared Mock Data for E2E Tests
 */

// User Profiles
export const MOCK_USERS = {
  lawyer: {
    id: 'user_lawyer001',
    email: 'lawyer@leh.dev',
    name: '김변호사',
    role: 'lawyer',
    status: 'active',
    created_at: '2025-01-01T00:00:00Z',
  },
  detective: {
    id: 'user_det001',
    email: 'detective@leh.dev',
    name: '오탐정',
    role: 'detective',
    status: 'active',
    created_at: '2025-01-01T00:00:00Z',
  },
  client: {
    id: 'user_client001',
    email: 'client@leh.dev',
    name: '홍길동',
    role: 'client',
    status: 'active',
    created_at: '2025-01-01T00:00:00Z',
  },
};

// Auth Responses
export const MOCK_AUTH_RESPONSE = (userRole: 'lawyer' | 'detective' | 'client') => ({
  access_token: 'mock_access_token_' + userRole,
  token_type: 'bearer',
  user: MOCK_USERS[userRole],
});

// Cases List
export const MOCK_CASES = [
  {
    id: 'case_001',
    case_number: '2025가합1234',
    title: '서울중앙지방법원 민사소송',
    client_name: '홍길동',
    status: 'open',
    type: 'civil',
    description: '부당해고 구제신청 사건',
    created_at: '2025-01-15T09:00:00Z',
    updated_at: '2025-01-20T14:30:00Z',
  },
  {
    id: 'case_002',
    case_number: '2025형제5678',
    title: '형사 고소 대리',
    client_name: '강감찬',
    status: 'investigation',
    type: 'criminal',
    description: '사기죄 고소장 작성 및 증거 수집',
    created_at: '2025-02-01T10:00:00Z',
    updated_at: '2025-02-05T11:20:00Z',
  },
];

// Single Case Detail
export const MOCK_CASE_DETAIL = {
  ...MOCK_CASES[0],
  client: MOCK_USERS.client,
  lawyer: MOCK_USERS.lawyer,
  members: [
    { user: MOCK_USERS.lawyer, role: 'lead' },
    { user: MOCK_USERS.client, role: 'client' },
  ],
  timeline: [
    {
      id: 'event_001',
      title: '소장 접수',
      date: '2025-01-15T09:00:00Z',
      type: 'court',
    },
  ],
};

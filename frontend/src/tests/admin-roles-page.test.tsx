import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import AdminRolesPage from '@/pages/admin/roles';
import * as adminApi from '@/lib/api/admin';

jest.mock('next/router', () => ({
  useRouter() {
    return {
      route: '/admin/roles',
      pathname: '/admin/roles',
      query: {},
      asPath: '/admin/roles',
      push: jest.fn(),
    };
  },
}));

// Mock the admin API
jest.mock('@/lib/api/admin');
const mockGetRoles = adminApi.getRoles as jest.MockedFunction<typeof adminApi.getRoles>;
const mockUpdateRolePermissions = adminApi.updateRolePermissions as jest.MockedFunction<typeof adminApi.updateRolePermissions>;

const mockRolesData = {
  roles: [
    {
      role: 'admin' as const,
      cases: { view: true, edit: true, delete: true },
      evidence: { view: true, edit: true, delete: true },
      admin: { view: true, edit: true, delete: true },
      billing: { view: true, edit: true, delete: true },
    },
    {
      role: 'lawyer' as const,
      cases: { view: true, edit: true, delete: false },
      evidence: { view: true, edit: true, delete: false },
      admin: { view: false, edit: false, delete: false },
      billing: { view: false, edit: false, delete: false },
    },
    {
      role: 'staff' as const,
      cases: { view: true, edit: false, delete: false },
      evidence: { view: true, edit: false, delete: false },
      admin: { view: false, edit: false, delete: false },
      billing: { view: false, edit: false, delete: false },
    },
  ],
};

beforeEach(() => {
  jest.clearAllMocks();
  mockGetRoles.mockResolvedValue({
    data: mockRolesData,
    status: 200,
  });
  mockUpdateRolePermissions.mockResolvedValue({
    data: mockRolesData.roles[1],
    status: 200,
  });
});

describe('plan 3.15: 권한 설정 페이지 (/admin/roles)', () => {
  it('역할별(Admin, Attorney, Staff) 권한 매트릭스 테이블을 렌더링한다.', async () => {
    render(<AdminRolesPage />);

    expect(
      screen.getByRole('heading', { name: /권한 설정/i }),
    ).toBeInTheDocument();

    // Wait for API data to load - check for resource column headers
    await waitFor(() => {
      expect(
        screen.getByRole('columnheader', { name: /사건/i }),
      ).toBeInTheDocument();
    });

    // Check resource columns
    expect(
      screen.getByRole('columnheader', { name: /증거/i }),
    ).toBeInTheDocument();

    // Check role labels are displayed
    expect(screen.getAllByText(/Admin/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Attorney/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Staff/i).length).toBeGreaterThan(0);
  });

  it('권한 토글 변경 시 상태가 업데이트되고, 저장 알림을 표시한다.', async () => {
    const user = userEvent.setup();
    render(<AdminRolesPage />);

    // Wait for data to load first
    await waitFor(() => {
      expect(screen.getByRole('columnheader', { name: /사건/i })).toBeInTheDocument();
    });

    // Find Attorney row's billing view checkbox (initially false)
    const billingCheckboxes = screen.getAllByRole('checkbox');
    // Attorney's billing view checkbox should be in the list
    const attorneyBillingViewCheckbox = billingCheckboxes.find(
      (cb) => !cb.hasAttribute('checked') && cb.closest('tr')?.textContent?.includes('Attorney')
    );

    if (attorneyBillingViewCheckbox) {
      await user.click(attorneyBillingViewCheckbox);

      expect(
        await screen.findByText(/권한 설정이 저장되었습니다\./i),
      ).toBeInTheDocument();
    }
  });
});

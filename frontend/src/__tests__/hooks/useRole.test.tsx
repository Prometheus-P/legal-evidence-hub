import { renderHook } from '@testing-library/react';
import type { ReactNode } from 'react';
import { useRole } from '@/hooks/useRole';
import AuthContext from '@/contexts/AuthContext';
import type { User, UserRole } from '@/types/user';

type AuthContextValue = React.ComponentProps<typeof AuthContext.Provider>['value'];

const USER_CACHE_KEY = 'userCache';

const mockLocalStorage = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: jest.fn((key: string) => store[key] || null),
    setItem: jest.fn((key: string, value: string) => {
      store[key] = value;
    }),
    removeItem: jest.fn((key: string) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    }),
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

const createContextValue = (overrides?: Partial<AuthContextValue>): AuthContextValue => ({
  user: null,
  role: null,
  isAuthenticated: false,
  isLoading: false,
  login: jest.fn(),
  logout: jest.fn(),
  refreshUser: jest.fn(),
  ...overrides,
});

const renderUseRole = (overrides?: Partial<AuthContextValue>) => {
  const wrapper = ({ children }: { children: ReactNode }) => (
    <AuthContext.Provider value={createContextValue(overrides)}>
      {children}
    </AuthContext.Provider>
  );

  return renderHook(() => useRole(), { wrapper });
};

describe('useRole Hook', () => {
  beforeEach(() => {
    mockLocalStorage.clear();
    jest.clearAllMocks();
  });

  const buildUser = (role: UserRole): User => ({
    id: `user-${role}`,
    email: `${role}@example.com`,
    name: `Test ${role}`,
    role,
    status: 'active',
    created_at: '2024-01-01T00:00:00Z',
  });

  describe('User detection', () => {
    it('returns null when context has no user', () => {
      const { result } = renderUseRole();

      expect(result.current.user).toBeNull();
      expect(result.current.role).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(result.current.isLoading).toBe(false);
    });

    it('returns context user when authenticated', () => {
      const mockUser = buildUser('lawyer');
      const { result } = renderUseRole({
        user: mockUser,
        role: mockUser.role,
        isAuthenticated: true,
      });

      expect(result.current.user).toEqual(mockUser);
      expect(result.current.role).toBe('lawyer');
      expect(result.current.isAuthenticated).toBe(true);
    });

    it('falls back to cached user when context empty', () => {
      const mockUser = buildUser('staff');
      mockLocalStorage.setItem(USER_CACHE_KEY, JSON.stringify(mockUser));

      const { result } = renderUseRole();

      expect(result.current.user).toEqual(mockUser);
      expect(result.current.role).toBe('staff');
      expect(result.current.isAuthenticated).toBe(true);
    });

    it('ignores invalid cache without crashing', () => {
      mockLocalStorage.setItem(USER_CACHE_KEY, 'not-json');

      const { result } = renderUseRole();

      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });
  });

  describe('Role flags', () => {
    const cases: Array<{
      role: UserRole;
      expectations: Partial<Record<keyof ReturnType<typeof useRole>, boolean>>;
    }> = [
      {
        role: 'admin',
        expectations: {
          isAdmin: true,
          isInternal: true,
          isExternal: false,
        },
      },
      {
        role: 'lawyer',
        expectations: {
          isLawyer: true,
          isInternal: true,
          isExternal: false,
        },
      },
      {
        role: 'staff',
        expectations: {
          isStaff: true,
          isInternal: true,
          isExternal: false,
        },
      },
      {
        role: 'client',
        expectations: {
          isClient: true,
          isInternal: false,
          isExternal: true,
        },
      },
      {
        role: 'detective',
        expectations: {
          isDetective: true,
          isInternal: false,
          isExternal: true,
        },
      },
    ];

    it.each(cases)('sets boolean flags for %s role', ({ role, expectations }) => {
      const mockUser = buildUser(role);
      const { result } = renderUseRole({
        user: mockUser,
        role,
        isAuthenticated: true,
      });

      expect(result.current.isAdmin).toBe(!!expectations.isAdmin);
      expect(result.current.isLawyer).toBe(!!expectations.isLawyer);
      expect(result.current.isStaff).toBe(!!expectations.isStaff);
      expect(result.current.isClient).toBe(!!expectations.isClient);
      expect(result.current.isDetective).toBe(!!expectations.isDetective);
      expect(result.current.isInternal).toBe(!!expectations.isInternal);
      expect(result.current.isExternal).toBe(!!expectations.isExternal);
    });
  });

  describe('Display helpers', () => {
    it('returns role display name for authenticated user', () => {
      const mockUser = buildUser('lawyer');
      const { result } = renderUseRole({
        user: mockUser,
        role: mockUser.role,
        isAuthenticated: true,
      });

      expect(result.current.roleDisplayName).toBe('변호사');
    });

    it('returns empty string when user missing', () => {
      const { result } = renderUseRole();

      expect(result.current.roleDisplayName).toBe('');
    });

    it('returns dashboard and portal paths per role', () => {
      const mockUser = buildUser('detective');
      const { result } = renderUseRole({
        user: mockUser,
        role: mockUser.role,
        isAuthenticated: true,
      });

      expect(result.current.dashboardPath).toBe('/detective/dashboard');
      expect(result.current.portalPath).toBe('/detective');
    });

    it('falls back to /login dashboard when unauthenticated', () => {
      const { result } = renderUseRole();
      expect(result.current.dashboardPath).toBe('/login');
    });
  });

  describe('Feature access', () => {
    it('allows admin to access everything', () => {
      const mockUser = buildUser('admin');
      const { result } = renderUseRole({
        user: mockUser,
        role: mockUser.role,
        isAuthenticated: true,
      });

      expect(result.current.hasAccess('any-feature')).toBe(true);
      expect(result.current.hasAccess('billing')).toBe(true);
    });

    it('allows lawyer features but not detective-only ones', () => {
      const mockUser = buildUser('lawyer');
      const { result } = renderUseRole({
        user: mockUser,
        role: mockUser.role,
        isAuthenticated: true,
      });

      expect(result.current.hasAccess('cases')).toBe(true);
      expect(result.current.hasAccess('calendar')).toBe(true);
      expect(result.current.hasAccess('field')).toBe(false);
    });

    it('denies access when user missing', () => {
      const { result } = renderUseRole();
      expect(result.current.hasAccess('cases')).toBe(false);
    });
  });

  describe('Portal access', () => {
    it('allows admin access to all portals', () => {
      const mockUser = buildUser('admin');
      const { result } = renderUseRole({
        user: mockUser,
        role: mockUser.role,
        isAuthenticated: true,
      });

      expect(result.current.canAccessPortal('admin')).toBe(true);
      expect(result.current.canAccessPortal('lawyer')).toBe(true);
      expect(result.current.canAccessPortal('client')).toBe(true);
      expect(result.current.canAccessPortal('detective')).toBe(true);
    });

    it('restricts client to client portal only', () => {
      const mockUser = buildUser('client');
      const { result } = renderUseRole({
        user: mockUser,
        role: mockUser.role,
        isAuthenticated: true,
      });

      expect(result.current.canAccessPortal('client')).toBe(true);
      expect(result.current.canAccessPortal('lawyer')).toBe(false);
    });

    it('denies all portals when unauthenticated', () => {
      const { result } = renderUseRole();

      expect(result.current.canAccessPortal('lawyer')).toBe(false);
      expect(result.current.canAccessPortal('client')).toBe(false);
    });
  });
});


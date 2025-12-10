/**
 * useAuth Hook Tests
 * Tests authentication context integration and hook functionality
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import type { ReactNode } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { AuthProvider, useAuth as useAuthContext } from '@/contexts/AuthContext';
import AuthContext from '@/contexts/AuthContext';
import type { User, UserRole } from '@/types/user';

// Mock next/navigation
const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

// Mock API calls
jest.mock('@/lib/api/auth', () => ({
  login: jest.fn(),
  logout: jest.fn(),
  getCurrentUser: jest.fn(),
}));

import { login as apiLogin, logout as apiLogout, getCurrentUser } from '@/lib/api/auth';

const mockApiLogin = apiLogin as jest.Mock;
const mockApiLogout = apiLogout as jest.Mock;
const mockGetCurrentUser = getCurrentUser as jest.Mock;

// Type for AuthContext value
type AuthContextValue = React.ComponentProps<typeof AuthContext.Provider>['value'];

const USER_CACHE_KEY = 'userCache';

// Mock localStorage
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
    _getStore: () => store,
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

// Mock document.cookie
let documentCookie = '';
Object.defineProperty(document, 'cookie', {
  get: () => documentCookie,
  set: (value: string) => {
    documentCookie = value;
  },
});

// Helper to build a mock user
const buildUser = (role: UserRole): User => ({
  id: `user-${role}`,
  email: `${role}@example.com`,
  name: `Test ${role}`,
  role,
  status: 'active',
  created_at: '2024-01-01T00:00:00Z',
});

// Helper to create mock context value
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

describe('useAuth Hook', () => {
  beforeEach(() => {
    mockLocalStorage.clear();
    documentCookie = '';
    jest.clearAllMocks();
    mockGetCurrentUser.mockResolvedValue({ data: null });
  });

  describe('Hook Wrapper Functionality', () => {
    it('provides getUser helper that returns current user', () => {
      const mockUser = buildUser('lawyer');
      const wrapper = ({ children }: { children: ReactNode }) => (
        <AuthContext.Provider value={createContextValue({ user: mockUser })}>
          {children}
        </AuthContext.Provider>
      );

      const { result } = renderHook(() => useAuth(), { wrapper });

      expect(result.current.getUser()).toEqual(mockUser);
    });

    it('getUser returns null when not authenticated', () => {
      const wrapper = ({ children }: { children: ReactNode }) => (
        <AuthContext.Provider value={createContextValue()}>
          {children}
        </AuthContext.Provider>
      );

      const { result } = renderHook(() => useAuth(), { wrapper });

      expect(result.current.getUser()).toBeNull();
    });

    it('provides refreshAuth as alias for refreshUser', () => {
      const mockRefreshUser = jest.fn();
      const wrapper = ({ children }: { children: ReactNode }) => (
        <AuthContext.Provider value={createContextValue({ refreshUser: mockRefreshUser })}>
          {children}
        </AuthContext.Provider>
      );

      const { result } = renderHook(() => useAuth(), { wrapper });

      result.current.refreshAuth();

      expect(mockRefreshUser).toHaveBeenCalledTimes(1);
    });

    it('spreads all context properties', () => {
      const mockUser = buildUser('admin');
      const mockLogin = jest.fn();
      const mockLogout = jest.fn();
      const mockRefreshUser = jest.fn();

      const wrapper = ({ children }: { children: ReactNode }) => (
        <AuthContext.Provider
          value={createContextValue({
            user: mockUser,
            role: mockUser.role,
            isAuthenticated: true,
            isLoading: false,
            login: mockLogin,
            logout: mockLogout,
            refreshUser: mockRefreshUser,
          })}
        >
          {children}
        </AuthContext.Provider>
      );

      const { result } = renderHook(() => useAuth(), { wrapper });

      expect(result.current.user).toEqual(mockUser);
      expect(result.current.role).toBe('admin');
      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.isLoading).toBe(false);
      expect(result.current.login).toBe(mockLogin);
      expect(result.current.logout).toBe(mockLogout);
    });
  });

  describe('Error Handling', () => {
    it('throws error when used outside AuthProvider', () => {
      // Suppress console.error for this test
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      expect(() => {
        renderHook(() => useAuthContext());
      }).toThrow('useAuth must be used within an AuthProvider');

      consoleSpy.mockRestore();
    });
  });
});

describe('AuthProvider Integration', () => {
  beforeEach(() => {
    mockLocalStorage.clear();
    documentCookie = '';
    jest.clearAllMocks();
    mockGetCurrentUser.mockResolvedValue({ data: null });
  });

  describe('Initial State', () => {
    it('starts with loading state', () => {
      mockGetCurrentUser.mockImplementation(() => new Promise(() => {})); // Never resolves

      const wrapper = ({ children }: { children: ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      );

      const { result } = renderHook(() => useAuthContext(), { wrapper });

      expect(result.current.isLoading).toBe(true);
      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
    });

    it('sets user when getCurrentUser returns data', async () => {
      const mockUser = {
        id: 'user-1',
        email: 'test@example.com',
        name: 'Test User',
        role: 'lawyer',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z',
      };

      mockGetCurrentUser.mockResolvedValue({ data: mockUser });

      const wrapper = ({ children }: { children: ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      );

      const { result } = renderHook(() => useAuthContext(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.user?.email).toBe('test@example.com');
      expect(result.current.role).toBe('lawyer');
      expect(result.current.isAuthenticated).toBe(true);
    });

    it('clears legacy localStorage tokens on init', async () => {
      mockLocalStorage.setItem('authToken', 'legacy-token');
      mockLocalStorage.setItem('user', JSON.stringify({ id: 'old' }));

      const wrapper = ({ children }: { children: ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      );

      renderHook(() => useAuthContext(), { wrapper });

      await waitFor(() => {
        expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('authToken');
        expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('user');
      });
    });
  });

  describe('Login Flow', () => {
    it('successfully logs in and redirects to dashboard', async () => {
      const mockLoginResponse = {
        data: {
          access_token: 'test-token',
          token_type: 'Bearer',
          user: {
            id: 'user-1',
            email: 'lawyer@example.com',
            name: 'Test Lawyer',
            role: 'lawyer',
          },
        },
      };

      mockApiLogin.mockResolvedValue(mockLoginResponse);
      mockGetCurrentUser.mockResolvedValue({ data: null });

      const wrapper = ({ children }: { children: ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      );

      const { result } = renderHook(() => useAuthContext(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      let loginResult: { success: boolean; error?: string };
      await act(async () => {
        loginResult = await result.current.login('lawyer@example.com', 'password');
      });

      expect(loginResult!.success).toBe(true);
      expect(mockApiLogin).toHaveBeenCalledWith('lawyer@example.com', 'password');
      expect(mockPush).toHaveBeenCalledWith('/lawyer/dashboard');
      expect(result.current.user?.email).toBe('lawyer@example.com');
    });

    it('returns error on login failure', async () => {
      mockApiLogin.mockResolvedValue({
        error: '이메일 또는 비밀번호가 올바르지 않습니다.',
        data: null,
      });
      mockGetCurrentUser.mockResolvedValue({ data: null });

      const wrapper = ({ children }: { children: ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      );

      const { result } = renderHook(() => useAuthContext(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      let loginResult: { success: boolean; error?: string };
      await act(async () => {
        loginResult = await result.current.login('wrong@example.com', 'wrong');
      });

      expect(loginResult!.success).toBe(false);
      expect(loginResult!.error).toBe('이메일 또는 비밀번호가 올바르지 않습니다.');
      expect(result.current.isAuthenticated).toBe(false);
    });

    it('handles login API exception', async () => {
      mockApiLogin.mockRejectedValue(new Error('Network error'));
      mockGetCurrentUser.mockResolvedValue({ data: null });

      const wrapper = ({ children }: { children: ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      );

      const { result } = renderHook(() => useAuthContext(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      let loginResult: { success: boolean; error?: string };
      await act(async () => {
        loginResult = await result.current.login('test@example.com', 'password');
      });

      expect(loginResult!.success).toBe(false);
      expect(loginResult!.error).toBe('로그인 중 오류가 발생했습니다.');
    });

    it('caches user info in localStorage after login', async () => {
      const mockLoginResponse = {
        data: {
          access_token: 'test-token',
          token_type: 'Bearer',
          user: {
            id: 'user-1',
            email: 'staff@example.com',
            name: 'Test Staff',
            role: 'staff',
          },
        },
      };

      mockApiLogin.mockResolvedValue(mockLoginResponse);
      mockGetCurrentUser.mockResolvedValue({ data: null });

      const wrapper = ({ children }: { children: ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      );

      const { result } = renderHook(() => useAuthContext(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await act(async () => {
        await result.current.login('staff@example.com', 'password');
      });

      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        USER_CACHE_KEY,
        expect.stringContaining('staff@example.com')
      );
    });
  });

  describe('Logout Flow', () => {
    it('clears user state and redirects to login', async () => {
      const mockUser = {
        id: 'user-1',
        email: 'test@example.com',
        name: 'Test User',
        role: 'lawyer',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z',
      };

      mockGetCurrentUser.mockResolvedValue({ data: mockUser });
      mockApiLogout.mockResolvedValue({});

      const wrapper = ({ children }: { children: ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      );

      const { result } = renderHook(() => useAuthContext(), { wrapper });

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true);
      });

      await act(async () => {
        await result.current.logout();
      });

      expect(mockApiLogout).toHaveBeenCalled();
      expect(result.current.user).toBeNull();
      expect(result.current.isAuthenticated).toBe(false);
      expect(mockPush).toHaveBeenCalledWith('/login');
    });

    it('clears localStorage on logout', async () => {
      mockGetCurrentUser.mockResolvedValue({ data: null });
      mockApiLogout.mockResolvedValue({});

      const wrapper = ({ children }: { children: ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      );

      const { result } = renderHook(() => useAuthContext(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await act(async () => {
        await result.current.logout();
      });

      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith(USER_CACHE_KEY);
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('authToken');
      expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('user');
    });

    it('clears state even if logout API fails', async () => {
      mockGetCurrentUser.mockResolvedValue({ data: { id: 'user-1', email: 'test@example.com', name: 'Test', role: 'lawyer', status: 'active' } });
      // Simulate logout API failure
      mockApiLogout.mockImplementation(() => Promise.reject(new Error('Network error')));

      const wrapper = ({ children }: { children: ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      );

      const { result } = renderHook(() => useAuthContext(), { wrapper });

      await waitFor(() => {
        expect(result.current.isAuthenticated).toBe(true);
      });

      // The logout function doesn't re-throw the error (uses try/finally),
      // so no catch is needed here. State should be cleared regardless.
      await act(async () => {
        try {
          await result.current.logout();
        } catch {
          // Expected - the error may bubble up from try/finally
        }
      });

      // Should still clear local state
      expect(result.current.user).toBeNull();
      expect(mockPush).toHaveBeenCalledWith('/login');
    });
  });

  describe('Refresh User', () => {
    it('refreshes user data from API', async () => {
      const initialUser = {
        id: 'user-1',
        email: 'test@example.com',
        name: 'Initial Name',
        role: 'lawyer',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z',
      };

      const updatedUser = {
        ...initialUser,
        name: 'Updated Name',
      };

      mockGetCurrentUser
        .mockResolvedValueOnce({ data: initialUser })
        .mockResolvedValueOnce({ data: updatedUser });

      const wrapper = ({ children }: { children: ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      );

      const { result } = renderHook(() => useAuthContext(), { wrapper });

      await waitFor(() => {
        expect(result.current.user?.name).toBe('Initial Name');
      });

      await act(async () => {
        await result.current.refreshUser();
      });

      await waitFor(() => {
        expect(result.current.user?.name).toBe('Updated Name');
      });
    });
  });

  describe('Role-based Redirects', () => {
    const roleTests = [
      { role: 'admin', expectedPath: '/admin/dashboard' },
      { role: 'lawyer', expectedPath: '/lawyer/dashboard' },
      { role: 'staff', expectedPath: '/lawyer/dashboard' },
      { role: 'client', expectedPath: '/client/dashboard' },
      { role: 'detective', expectedPath: '/detective/dashboard' },
    ];

    it.each(roleTests)('redirects $role to $expectedPath on login', async ({ role, expectedPath }) => {
      const mockLoginResponse = {
        data: {
          access_token: 'test-token',
          token_type: 'Bearer',
          user: {
            id: 'user-1',
            email: `${role}@example.com`,
            name: `Test ${role}`,
            role,
          },
        },
      };

      mockApiLogin.mockResolvedValue(mockLoginResponse);
      mockGetCurrentUser.mockResolvedValue({ data: null });
      mockPush.mockClear();

      const wrapper = ({ children }: { children: ReactNode }) => (
        <AuthProvider>{children}</AuthProvider>
      );

      const { result } = renderHook(() => useAuthContext(), { wrapper });

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      await act(async () => {
        await result.current.login(`${role}@example.com`, 'password');
      });

      expect(mockPush).toHaveBeenCalledWith(expectedPath);
    });
  });
});

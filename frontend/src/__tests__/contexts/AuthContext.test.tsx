/**
 * AuthContext Tests
 * Direct tests for the AuthProvider component and context functionality
 *
 * Covers:
 * - Provider initialization
 * - Authentication state management
 * - Login/logout flows
 * - Token refresh logic
 * - Error handling
 */

import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { ReactNode } from 'react';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';

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

// Mock sessionStorage
const mockSessionStorage = (() => {
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

Object.defineProperty(window, 'sessionStorage', {
  value: mockSessionStorage,
});

// Mock document.cookie
let documentCookie = '';
Object.defineProperty(document, 'cookie', {
  get: () => documentCookie,
  set: (value: string) => {
    documentCookie = value;
  },
  configurable: true,
});

// Test component that uses auth context
function TestConsumer() {
  const { user, role, isAuthenticated, isLoading, login, logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
    } catch {
      // Ignore logout errors in test - state should still be cleared
    }
  };

  return (
    <div>
      <span data-testid="loading">{isLoading ? 'loading' : 'ready'}</span>
      <span data-testid="authenticated">{isAuthenticated ? 'yes' : 'no'}</span>
      <span data-testid="user">{user?.email || 'none'}</span>
      <span data-testid="role">{role || 'none'}</span>
      <button onClick={() => login('test@example.com', 'password')}>Login</button>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.clear();
    mockSessionStorage.clear();
    documentCookie = '';
    mockGetCurrentUser.mockResolvedValue({ data: null });
  });

  describe('Provider Initialization', () => {
    it('renders children correctly', async () => {
      render(
        <AuthProvider>
          <div data-testid="child">Test Child</div>
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('child')).toHaveTextContent('Test Child');
      });
    });

    it('starts with loading state', () => {
      mockGetCurrentUser.mockImplementation(() => new Promise(() => {})); // Never resolves

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      );

      expect(screen.getByTestId('loading')).toHaveTextContent('loading');
      expect(screen.getByTestId('authenticated')).toHaveTextContent('no');
    });

    it('transitions to ready state after auth check', async () => {
      mockGetCurrentUser.mockResolvedValue({ data: null });

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready');
      });
    });

    it('loads authenticated user from API', async () => {
      const mockUser = {
        id: 'user-1',
        email: 'lawyer@example.com',
        name: 'Test Lawyer',
        role: 'lawyer',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z',
      };

      mockGetCurrentUser.mockResolvedValue({ data: mockUser });

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('authenticated')).toHaveTextContent('yes');
        expect(screen.getByTestId('user')).toHaveTextContent('lawyer@example.com');
        expect(screen.getByTestId('role')).toHaveTextContent('lawyer');
      });
    });

    it('clears legacy localStorage tokens on init', async () => {
      mockLocalStorage.setItem('authToken', 'old-token');
      mockLocalStorage.setItem('user', '{"id": "old"}');

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('authToken');
        expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('user');
      });
    });

    it('uses cached user when justLoggedIn flag is set', async () => {
      const cachedUser = {
        id: 'cached-user',
        email: 'cached@example.com',
        name: 'Cached User',
        role: 'staff',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z',
      };

      mockSessionStorage.setItem('justLoggedIn', 'true');
      mockLocalStorage.setItem('userCache', JSON.stringify(cachedUser));

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('cached@example.com');
      });

      // Should not call getCurrentUser when justLoggedIn is set
      expect(mockGetCurrentUser).not.toHaveBeenCalled();
    });
  });

  describe('Login Flow', () => {
    it('successfully logs in a user', async () => {
      const user = userEvent.setup();
      const mockLoginResponse = {
        data: {
          access_token: 'test-token',
          token_type: 'Bearer',
          user: {
            id: 'user-1',
            email: 'test@example.com',
            name: 'Test User',
            role: 'lawyer',
          },
        },
      };

      mockApiLogin.mockResolvedValue(mockLoginResponse);

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready');
      });

      await user.click(screen.getByText('Login'));

      await waitFor(() => {
        expect(screen.getByTestId('authenticated')).toHaveTextContent('yes');
        expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
      });

      expect(mockApiLogin).toHaveBeenCalledWith('test@example.com', 'password');
    });

    it('caches user info in localStorage after login', async () => {
      const user = userEvent.setup();
      const mockLoginResponse = {
        data: {
          access_token: 'test-token',
          token_type: 'Bearer',
          user: {
            id: 'user-1',
            email: 'staff@example.com',
            name: 'Staff User',
            role: 'staff',
          },
        },
      };

      mockApiLogin.mockResolvedValue(mockLoginResponse);

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready');
      });

      await user.click(screen.getByText('Login'));

      await waitFor(() => {
        expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
          'userCache',
          expect.stringContaining('staff@example.com')
        );
      });
    });

    it('sets justLoggedIn flag in sessionStorage', async () => {
      const user = userEvent.setup();
      const mockLoginResponse = {
        data: {
          access_token: 'test-token',
          token_type: 'Bearer',
          user: {
            id: 'user-1',
            email: 'test@example.com',
            name: 'Test User',
            role: 'lawyer',
          },
        },
      };

      mockApiLogin.mockResolvedValue(mockLoginResponse);

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready');
      });

      await user.click(screen.getByText('Login'));

      await waitFor(() => {
        expect(mockSessionStorage.setItem).toHaveBeenCalledWith('justLoggedIn', 'true');
      });
    });

    it('handles login API error', async () => {
      const user = userEvent.setup();
      mockApiLogin.mockResolvedValue({
        error: 'Invalid credentials',
        data: null,
      });

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready');
      });

      await user.click(screen.getByText('Login'));

      await waitFor(() => {
        expect(screen.getByTestId('authenticated')).toHaveTextContent('no');
      });
    });

    it('handles login API exception', async () => {
      const user = userEvent.setup();
      mockApiLogin.mockRejectedValue(new Error('Network error'));

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready');
      });

      await user.click(screen.getByText('Login'));

      await waitFor(() => {
        expect(screen.getByTestId('authenticated')).toHaveTextContent('no');
      });
    });
  });

  describe('Logout Flow', () => {
    it('clears user state on logout', async () => {
      const user = userEvent.setup();
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

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('authenticated')).toHaveTextContent('yes');
      });

      await user.click(screen.getByText('Logout'));

      await waitFor(() => {
        expect(screen.getByTestId('authenticated')).toHaveTextContent('no');
        expect(screen.getByTestId('user')).toHaveTextContent('none');
      });
    });

    it('redirects to login page on logout', async () => {
      const user = userEvent.setup();
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

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('authenticated')).toHaveTextContent('yes');
      });

      await user.click(screen.getByText('Logout'));

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/login');
      });
    });

    it('clears localStorage on logout', async () => {
      const user = userEvent.setup();
      mockGetCurrentUser.mockResolvedValue({ data: null });
      mockApiLogout.mockResolvedValue({});

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready');
      });

      await user.click(screen.getByText('Logout'));

      await waitFor(() => {
        expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('userCache');
        expect(mockLocalStorage.removeItem).toHaveBeenCalledWith('accessToken');
      });
    });

    it('clears state even if logout API fails', async () => {
      const user = userEvent.setup();
      const mockUser = {
        id: 'user-1',
        email: 'test@example.com',
        name: 'Test User',
        role: 'lawyer',
        status: 'active',
        created_at: '2024-01-01T00:00:00Z',
      };

      mockGetCurrentUser.mockResolvedValue({ data: mockUser });
      mockApiLogout.mockRejectedValue(new Error('Network error'));

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('authenticated')).toHaveTextContent('yes');
      });

      await user.click(screen.getByText('Logout'));

      // Should still clear state despite API error
      await waitFor(() => {
        expect(screen.getByTestId('authenticated')).toHaveTextContent('no');
        expect(mockPush).toHaveBeenCalledWith('/login');
      });
    });
  });

  describe('Error Handling', () => {
    it('handles getCurrentUser API error gracefully', async () => {
      mockGetCurrentUser.mockRejectedValue(new Error('API Error'));

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready');
        expect(screen.getByTestId('authenticated')).toHaveTextContent('no');
      });
    });

    it('clears user data cookie on auth check failure', async () => {
      mockGetCurrentUser.mockRejectedValue(new Error('Auth failed'));

      render(
        <AuthProvider>
          <TestConsumer />
        </AuthProvider>
      );

      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('ready');
      });

      // Cookie should be cleared (set to expired)
      expect(documentCookie).toContain('expires=Thu, 01 Jan 1970');
    });
  });

  describe('Context Error Boundary', () => {
    it('throws error when useAuth is used outside AuthProvider', () => {
      // Suppress console.error for this test
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      expect(() => {
        render(<TestConsumer />);
      }).toThrow('useAuth must be used within an AuthProvider');

      consoleSpy.mockRestore();
    });
  });
});

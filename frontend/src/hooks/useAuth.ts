/**
 * Authentication Hook
 * Handles login state and user info using HTTP-only cookies
 * Tokens are stored in HTTP-only cookies by the backend (XSS protection)
 */

import { useCallback, useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { getCurrentUser, logout as logoutApi, UserInfo } from '@/lib/api/auth';

// App version - update this when deploying new versions
const APP_VERSION = '0.3.0';
const APP_VERSION_KEY = 'appVersion';
const USER_CACHE_KEY = 'userCache'; // Cached user info (not sensitive)

export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

export function useAuth() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);

  // Check version - clear cache if version changed
  const checkVersion = useCallback(() => {
    if (typeof window === 'undefined') return;

    const storedVersion = localStorage.getItem(APP_VERSION_KEY);

    if (storedVersion && storedVersion !== APP_VERSION) {
      console.log(`App version changed: ${storedVersion} -> ${APP_VERSION}. Clearing cache.`);
      localStorage.removeItem(USER_CACHE_KEY);
    }

    localStorage.setItem(APP_VERSION_KEY, APP_VERSION);
  }, []);

  // Verify authentication by calling /auth/me API
  const verifyAuth = useCallback(async (): Promise<boolean> => {
    try {
      const response = await getCurrentUser();

      if (response.error || !response.data) {
        setIsAuthenticated(false);
        setUser(null);
        localStorage.removeItem(USER_CACHE_KEY);
        return false;
      }

      const userData: User = {
        id: response.data.id,
        email: response.data.email,
        name: response.data.name,
        role: response.data.role,
      };

      setIsAuthenticated(true);
      setUser(userData);

      // Cache user info for display (not for auth)
      localStorage.setItem(USER_CACHE_KEY, JSON.stringify(userData));

      return true;
    } catch {
      setIsAuthenticated(false);
      setUser(null);
      localStorage.removeItem(USER_CACHE_KEY);
      return false;
    }
  }, []);

  // Initialize auth state
  useEffect(() => {
    const initAuth = async () => {
      checkVersion();

      // Try to load cached user first for faster initial render
      const cachedUser = localStorage.getItem(USER_CACHE_KEY);
      if (cachedUser) {
        try {
          const parsed = JSON.parse(cachedUser);
          setUser(parsed);
          setIsAuthenticated(true);
        } catch {
          // Invalid cache, will be refreshed
        }
      }

      // Verify with server (cookie-based auth)
      await verifyAuth();
      setIsLoading(false);
    };

    initAuth();
  }, [checkVersion, verifyAuth]);

  // Logout handler
  const logout = useCallback(async () => {
    try {
      // Call logout API to clear HTTP-only cookies
      await logoutApi();
    } catch (error) {
      console.error('Logout API error:', error);
    }

    // Clear local state
    setIsAuthenticated(false);
    setUser(null);
    localStorage.removeItem(USER_CACHE_KEY);

    router.push('/login');
  }, [router]);

  // Get user info (from state)
  const getUser = useCallback((): User | null => {
    return user;
  }, [user]);

  // Refresh auth state
  const refreshAuth = useCallback(async () => {
    setIsLoading(true);
    await verifyAuth();
    setIsLoading(false);
  }, [verifyAuth]);

  return {
    isAuthenticated,
    isLoading,
    user,
    logout,
    getUser,
    refreshAuth,
    verifyAuth,
  };
}

export default useAuth;

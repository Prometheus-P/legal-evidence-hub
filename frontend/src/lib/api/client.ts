/**
 * API Client Configuration
 * Base API client for making HTTP requests to the backend
 * Uses HTTP-only cookies for authentication (XSS protection)
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

/**
 * Generic API request function
 * Authentication is handled via HTTP-only cookies (set by backend)
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const url = `${API_BASE_URL}${endpoint}`;

    const response = await fetch(url, {
      ...options,
      credentials: 'include', // Include cookies for authentication
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    // Handle empty responses (e.g., 204 No Content)
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let data: any = null;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      const text = await response.text();
      if (text) {
        data = JSON.parse(text);
      }
    }

    if (!response.ok) {
      // Handle both error formats: { error: { message: "..." } } and { detail: "..." }
      const errorMessage = data?.error?.message || data?.detail || 'An error occurred';

      // Handle 401 Unauthorized - redirect to login
      if (response.status === 401 && typeof window !== 'undefined') {
        // Don't redirect if already on login/signup/forgot-password pages
        const currentPath = window.location.pathname;
        const authPaths = ['/login', '/signup', '/forgot-password', '/reset-password'];
        if (!authPaths.some(path => currentPath.startsWith(path))) {
          window.location.href = '/login';
        }
      }

      return {
        error: errorMessage,
        status: response.status,
      };
    }

    return {
      data,
      status: response.status,
    };
  } catch (error) {
    return {
      error: error instanceof Error ? error.message : 'Network error',
      status: 0,
    };
  }
}

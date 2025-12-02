/**
 * Admin API Client
 * Handles admin operations including role/permission management
 */

import { apiRequest, ApiResponse } from './client';

// ============================================
// Types
// ============================================

export type UserRole = 'admin' | 'lawyer' | 'staff';

export interface ResourcePermission {
  view: boolean;
  edit: boolean;
  delete: boolean;
}

export interface RolePermissions {
  role: UserRole;
  cases: ResourcePermission;
  evidence: ResourcePermission;
  admin: ResourcePermission;
  billing: ResourcePermission;
}

export interface RolePermissionsResponse {
  roles: RolePermissions[];
}

export interface UpdateRolePermissionsRequest {
  cases: ResourcePermission;
  evidence: ResourcePermission;
  admin: ResourcePermission;
  billing: ResourcePermission;
}

// ============================================
// API Functions
// ============================================

/**
 * Get all roles with their permissions
 */
export async function getRoles(): Promise<ApiResponse<RolePermissionsResponse>> {
  return apiRequest<RolePermissionsResponse>('/admin/roles', {
    method: 'GET',
  });
}

/**
 * Update permissions for a specific role
 */
export async function updateRolePermissions(
  role: UserRole,
  permissions: UpdateRolePermissionsRequest
): Promise<ApiResponse<RolePermissions>> {
  return apiRequest<RolePermissions>(`/admin/roles/${role}/permissions`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(permissions),
  });
}

import Head from 'next/head';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { Loader2 } from 'lucide-react';
import {
  getRoles,
  updateRolePermissions,
  RolePermissions,
  ResourcePermission,
  UserRole,
} from '@/lib/api/admin';

type ResourceKey = 'cases' | 'evidence' | 'admin' | 'billing';
type PermissionType = 'view' | 'edit' | 'delete';

const RESOURCE_LABELS: Record<ResourceKey, string> = {
  cases: '사건',
  evidence: '증거',
  admin: 'Admin 메뉴',
  billing: 'Billing',
};

const PERMISSION_LABELS: Record<PermissionType, string> = {
  view: '보기',
  edit: '편집',
  delete: '삭제',
};

const ROLE_LABELS: Record<UserRole, string> = {
  admin: 'Admin',
  lawyer: 'Attorney',
  staff: 'Staff',
};

export default function AdminRolesPage() {
  const [roles, setRoles] = useState<RolePermissions[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saveMessage, setSaveMessage] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  const resourceKeys = useMemo(
    () => Object.keys(RESOURCE_LABELS) as ResourceKey[],
    [],
  );

  const permissionTypes = useMemo(
    () => Object.keys(PERMISSION_LABELS) as PermissionType[],
    [],
  );

  // Fetch roles from API
  const fetchRoles = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await getRoles();
      if (result.error) {
        setError(result.error);
      } else if (result.data) {
        setRoles(result.data.roles);
      }
    } catch (err) {
      setError('권한 정보를 불러오는데 실패했습니다.');
      console.error('Failed to fetch roles:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRoles();
  }, [fetchRoles]);

  const handleToggle = async (
    role: UserRole,
    resource: ResourceKey,
    permission: PermissionType
  ) => {
    // Find current role permissions
    const currentRole = roles.find((r) => r.role === role);
    if (!currentRole) return;

    // Create updated permissions
    const updatedPermissions: Record<ResourceKey, ResourcePermission> = {
      cases: { ...currentRole.cases },
      evidence: { ...currentRole.evidence },
      admin: { ...currentRole.admin },
      billing: { ...currentRole.billing },
    };

    // Toggle the specific permission
    updatedPermissions[resource][permission] = !updatedPermissions[resource][permission];

    // Optimistic update
    setRoles((prev) =>
      prev.map((r) =>
        r.role === role
          ? { ...r, ...updatedPermissions }
          : r
      )
    );

    setIsSaving(true);
    setSaveMessage('');

    try {
      const result = await updateRolePermissions(role, updatedPermissions);

      if (result.error) {
        // Revert on error
        setRoles((prev) =>
          prev.map((r) =>
            r.role === role ? currentRole : r
          )
        );
        setSaveMessage(`오류: ${result.error}`);
      } else {
        setSaveMessage('권한 설정이 저장되었습니다.');
      }
    } catch (err) {
      // Revert on error
      setRoles((prev) =>
        prev.map((r) =>
          r.role === role ? currentRole : r
        )
      );
      setSaveMessage('권한 저장에 실패했습니다.');
      console.error('Failed to update permissions:', err);
    } finally {
      setIsSaving(false);
      // Clear message after 3 seconds
      setTimeout(() => setSaveMessage(''), 3000);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      <Head>
        <title>권한 설정 | Legal Evidence Hub</title>
      </Head>

      <header className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-6 py-5 flex items-center justify-between">
          <div>
            <p className="text-xs text-gray-500 uppercase tracking-wide">
              Admin
            </p>
            <h1 className="text-2xl font-bold text-secondary">
              권한 설정
            </h1>
            <p className="text-sm text-neutral-600 mt-1">
              역할별 권한 매트릭스를 통해 Admin, Attorney, Staff 권한을 관리합니다.
            </p>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8 space-y-4">
        <section
          aria-label="역할별 권한 매트릭스"
          className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6"
        >
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-gray-900">
              역할별 권한 매트릭스
            </h2>
            <p className="text-sm text-neutral-600 mt-1">
              각 역할별로 리소스 접근 및 관리자 기능 권한을 세밀하게 제어합니다.
            </p>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-6 h-6 text-gray-400 animate-spin" />
              <span className="ml-2 text-gray-500">권한 정보를 불러오는 중...</span>
            </div>
          ) : error ? (
            <div className="text-center py-8 text-red-500">
              <p>{error}</p>
              <button
                onClick={fetchRoles}
                className="mt-2 text-sm text-blue-600 hover:underline"
              >
                다시 시도
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 border border-gray-100 rounded-lg bg-white text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th
                      scope="col"
                      className="px-4 py-3 text-left text-xs font-semibold text-neutral-600 uppercase tracking-wider"
                    >
                      역할
                    </th>
                    {resourceKeys.map((resource) => (
                      <th
                        key={resource}
                        scope="col"
                        colSpan={3}
                        className="px-4 py-3 text-center text-xs font-semibold text-neutral-600 uppercase tracking-wider border-l border-gray-200"
                      >
                        {RESOURCE_LABELS[resource]}
                      </th>
                    ))}
                  </tr>
                  <tr>
                    <th scope="col" className="px-4 py-2"></th>
                    {resourceKeys.map((resource) =>
                      permissionTypes.map((perm) => (
                        <th
                          key={`${resource}-${perm}`}
                          scope="col"
                          className={`px-2 py-2 text-center text-xs text-gray-500 ${
                            perm === 'view' ? 'border-l border-gray-200' : ''
                          }`}
                        >
                          {PERMISSION_LABELS[perm]}
                        </th>
                      ))
                    )}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-100">
                  {roles.map((role) => (
                    <tr
                      key={role.role}
                      className="hover:bg-gray-50"
                    >
                      <td className="px-4 py-3 font-medium text-gray-900">
                        {ROLE_LABELS[role.role]}
                      </td>
                      {resourceKeys.map((resource) =>
                        permissionTypes.map((perm) => {
                          const label = `${ROLE_LABELS[role.role]} ${RESOURCE_LABELS[resource]} ${PERMISSION_LABELS[perm]}`;
                          const isChecked = role[resource][perm];
                          return (
                            <td
                              key={`${resource}-${perm}`}
                              className={`px-2 py-3 text-center ${
                                perm === 'view' ? 'border-l border-gray-200' : ''
                              }`}
                            >
                              <input
                                type="checkbox"
                                aria-label={label}
                                className="h-4 w-4 text-accent focus:ring-accent border-gray-300 rounded disabled:opacity-50"
                                checked={isChecked}
                                onChange={() => handleToggle(role.role, resource, perm)}
                                disabled={isSaving}
                              />
                            </td>
                          );
                        })
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {saveMessage && (
            <div
              className={`mt-4 rounded-md px-4 py-3 text-sm ${
                saveMessage.startsWith('오류')
                  ? 'bg-red-50 text-red-700'
                  : 'bg-accent/10 text-secondary'
              }`}
            >
              {saveMessage}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

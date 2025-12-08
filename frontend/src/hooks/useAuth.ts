import { useAuth as useAuthContext } from '@/contexts/AuthContext';

export function useAuth() {
  const auth = useAuthContext();

  return {
    ...auth,
    getUser: () => auth.user,
    refreshAuth: auth.refreshUser,
  };
}

export default useAuth;

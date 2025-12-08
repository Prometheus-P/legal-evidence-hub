'use client';

import { ReactNode } from 'react';
import { AuthProvider } from '@/contexts/AuthContext';

interface Props {
  children: ReactNode;
}

export function AppProviders({ children }: Props) {
  return <AuthProvider>{children}</AuthProvider>;
}

export default AppProviders;

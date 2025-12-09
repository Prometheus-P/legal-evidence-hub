'use client';

import { ReactNode } from 'react';
import { AuthProvider } from '@/contexts/AuthContext';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { CommandPalette } from '@/components/shared/CommandPalette';
import { KeyboardShortcutsHelp } from '@/components/shared/KeyboardShortcutsHelp';

interface Props {
  children: ReactNode;
}

export function AppProviders({ children }: Props) {
  return (
    <ThemeProvider defaultTheme="system">
      <AuthProvider>
        {children}
        <CommandPalette />
        <KeyboardShortcutsHelp />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default AppProviders;

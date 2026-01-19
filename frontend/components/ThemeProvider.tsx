"use client";

import * as React from "react";
import { ThemeProvider as NextThemesProvider } from "next-themes";

interface ThemeProviderProps {
  children: React.ReactNode;
  defaultTheme?: "light" | "dark" | "system";
  storageKey?: string;
}

/**
 * ThemeProvider component that wraps the application to provide theme context and persistence.
 * 
 * Features:
 * - Reads system preference on first load
 * - Persists user selection to localStorage
 * - Provides theme context to all child components
 * - Prevents flash of unstyled content (FOUC)
 * 
 * @param children - React components to wrap with theme context
 * @param defaultTheme - Default theme to use ('light', 'dark', or 'system'). Defaults to 'system'
 * @param storageKey - localStorage key for persisting theme preference. Defaults to 'decisiontrace-theme'
 */
export function ThemeProvider({
  children,
  defaultTheme = "system",
  storageKey = "decisiontrace-theme",
}: ThemeProviderProps) {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme={defaultTheme}
      enableSystem={true}
      storageKey={storageKey}
      disableTransitionOnChange={false}
    >
      {children}
    </NextThemesProvider>
  );
}

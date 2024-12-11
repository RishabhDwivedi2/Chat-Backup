// src/hooks/useThemeManager.ts

import { useEffect } from 'react';
import { removeThemeClasses } from '@/config/themeConfig';
import type { ThemeColor, ThemeMode } from '@/config/themeConfig';

interface UseThemeManagerProps {
  color: ThemeColor;
  mode: ThemeMode;
  elementId?: string;
}

export const useThemeManager = ({ color, mode, elementId = 'theme-root' }: UseThemeManagerProps) => {
  useEffect(() => {
    const element = elementId === 'root' 
      ? document.documentElement 
      : document.getElementById(elementId);
      
    if (!element) return;

    removeThemeClasses(element);
    element.classList.add(color.toLowerCase());
    element.classList.add(mode.toLowerCase());
  }, [color, mode, elementId]);
};
// File: src/store/themeStore.ts

import create from 'zustand';
import { persist } from 'zustand/middleware';

type ThemeState = {
  customColor: string;
  mode: string;
  setCustomColor: (color: string) => void;
  setMode: (mode: string) => void;
};

const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      customColor: 'Zinc',
      mode: 'light',
      setCustomColor: (color: string) => set({ customColor: color }),
      setMode: (mode: string) => set({ mode: mode }),
    }),
    {
      name: 'theme-storage',
    }
  )
);

export default useThemeStore;
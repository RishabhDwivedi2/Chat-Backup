// src/store/profileStore.ts

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type UserProfile = 'Debtor' | 'FI Admin' | 'Resohub Admin' | 'Deltabots Admin' | null;

interface ProfileState {
  profile: UserProfile;
  userName: string | null;
  color: string;
  mode: string;
  setProfile: (profile: UserProfile) => void;
  setUserName: (name: string) => void;
  setColor: (color: string) => void;
  setMode: (mode: string) => void;
  isHydrated: boolean;
  setIsHydrated: (state: boolean) => void;
}

const useProfileStore = create<ProfileState>()(
  persist(
    (set) => ({
      profile: null,
      userName: null,
      color: 'zinc',
      mode: 'light',
      setProfile: (profile: UserProfile) => set({ profile }),
      setUserName: (name: string) => set({ userName: name }),
      setColor: (color: string) => set({ color }),
      setMode: (mode: string) => set({ mode }),
      isHydrated: false,
      setIsHydrated: (state: boolean) => set({ isHydrated: state }),
    }),
    {
      name: 'user-profile-storage',
      partialize: (state) => ({
        profile: state.profile,
        userName: state.userName,
        color: state.color,
        mode: state.mode,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.setIsHydrated(true);
        }
      },
    }
  )
);

export default useProfileStore;

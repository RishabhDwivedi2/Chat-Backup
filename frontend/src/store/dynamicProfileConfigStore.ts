// src/store/dynamicProfileConfigStore.ts

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { ProfileConfig, UserProfile, PanelType } from '@/config/profileConfig';

interface DynamicProfileConfigState {
  configs: Record<UserProfile, ProfileConfig>;
  configSources: Record<UserProfile, UserProfile>;
  updateConfig: (profile: UserProfile, newConfig: Partial<ProfileConfig>) => void;
  resetToDefault: () => void;
  saveChanges: () => void;
  getConfigSource: (profile: UserProfile) => UserProfile;
  setConfigSource: (profile: UserProfile, source: UserProfile) => void;
  migrateConfigs: () => void;
}

const defaultConfigs: Record<UserProfile, ProfileConfig> = {
  Debtor: {
    panels: ['ChatContainer', 'ChatControls'],
    maxPanels: 2,
    displayName: 'Debtor',
    headerPanels: ['ChatControls'],
    showSettings: false
  },
  'FI Admin': {
    panels: ['ChatContainer', 'ChatControls', 'ChatArtifacts'],
    maxPanels: 3,
    exclusivePanels: [['ChatControls', 'ChatArtifacts']],
    displayName: 'FI Admin',
    headerPanels: ['ChatControls'],
    showSettings: false
  },
  'Resohub Admin': {
    panels: ['ChatContainer', 'ChatControls', 'ChatArtifacts', 'ChatHistory'],
    maxPanels: 4,
    exclusivePanels: [['ChatControls', 'ChatArtifacts']],
    displayName: 'Resohub Admin',
    headerPanels: ['ChatControls', 'ChatHistory'],
    showSettings: false
  },
  'Deltabots Admin': {
    panels: ['ChatContainer', 'ChatControls', 'ChatArtifacts', 'ChatHistory', 'ChatProcessor'],
    maxPanels: 4,
    displayName: 'Deltabots Admin',
    headerPanels: ['ChatControls', 'ChatArtifacts', 'ChatHistory', 'ChatProcessor'],
    showSettings: true
  }
};

const useDynamicProfileConfigStore = create<DynamicProfileConfigState>()(
  persist(
    (set, get) => ({
      configs: defaultConfigs,
      configSources: {
        Debtor: 'Debtor',
        'FI Admin': 'FI Admin',
        'Resohub Admin': 'Resohub Admin',
        'Deltabots Admin': 'Deltabots Admin',
      },
      updateConfig: (profile, newConfig) => set((state) => ({
        configs: {
          ...state.configs,
          [profile]: { ...state.configs[profile], ...newConfig }
        }
      })),
      resetToDefault: () => set({ configs: defaultConfigs, configSources: {
        Debtor: 'Debtor',
        'FI Admin': 'FI Admin',
        'Resohub Admin': 'Resohub Admin',
        'Deltabots Admin': 'Deltabots Admin',
      } }),
      saveChanges: () => {
        console.log("Changes saved:", get().configs);
      },
      getConfigSource: (profile) => get().configSources[profile],
      setConfigSource: (profile, source) => set((state) => ({
        configSources: {
          ...state.configSources,
          [profile]: source
        }
      })),
      migrateConfigs: () => set((state) => {
        const oldToNewMapping = {
          PC1: 'Debtor',
          PC2: 'FI Admin',
          PC3: 'Resohub Admin',
          PC4: 'Deltabots Admin'
        };
        const newConfigs = {} as Record<UserProfile, ProfileConfig>;
        Object.entries(state.configs).forEach(([key, value]) => {
          const newKey = oldToNewMapping[key as keyof typeof oldToNewMapping] || key;
          newConfigs[newKey as UserProfile] = value;
        });
        return { configs: newConfigs };
      }),
    }),
    {
      name: 'dynamic-profile-config-storage',
    }
  )
);

export default useDynamicProfileConfigStore;
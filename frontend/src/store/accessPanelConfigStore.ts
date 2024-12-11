// File: src/stores/accessPanelConfigStore.ts

import { create } from 'zustand';
import { profileConfig, UserProfile, ProfileConfig } from '@/config/profileConfig';

interface PanelConfigState {
  panelConfig: Record<UserProfile, ProfileConfig>;
}

const usePanelConfigStore = create<PanelConfigState>()(() => ({
  panelConfig: profileConfig
}));

export default usePanelConfigStore;
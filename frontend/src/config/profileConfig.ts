// File: src/config/profileConfig.ts

// This file defines user profiles and their associated panel configurations.
// Each profile has specific panels they can access, maximum panels allowed,
// and any exclusive panel groups that restrict access to certain panels.

export type UserProfile = 'Debtor' | 'FI Admin' | 'Resohub Admin' | 'Deltabots Admin';

export type PanelType = 'ChatContainer' | 'ChatControls' | 'ChatArtifacts' | 'ChatHistory' | 'ChatProcessor';

export interface ProfileConfig {
    panels: PanelType[];
    maxPanels: number;
    exclusivePanels?: PanelType[][];
    displayName: string;
    headerPanels: PanelType[];
    showSettings: boolean;
}
  
export const profileConfig: Record<UserProfile, ProfileConfig> = {
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
// Access functions for panel management
export const getPanelAccess = (profile: UserProfile): PanelType[] => {
    return profileConfig[profile].panels; // Returns accessible panels for the profile
};

export const getMaxPanels = (profile: UserProfile): number => {
    return profileConfig[profile].maxPanels; // Returns max panels allowed for the profile
};

export const getExclusivePanels = (profile: UserProfile): PanelType[][] | undefined => {
    return profileConfig[profile].exclusivePanels; // Returns exclusive panel groups
};

export const getDisplayName = (profile: UserProfile): string => {
    return profileConfig[profile].displayName; // Returns display name for the profile
};

export const hasAccessToPanel = (profile: UserProfile, panel: PanelType): boolean => {
    return profileConfig[profile].panels.includes(panel); // Checks if the profile has access to a specific panel
};

export const hasMinimumProfileLevel = (profile: UserProfile, minLevel: number): boolean => {
    const profileLevels = Object.keys(profileConfig);
    const currentLevel = profileLevels.indexOf(profile);
    return currentLevel >= minLevel - 1; // Checks if the profile meets the minimum level requirement
};

// Related files:
// - @accessPanelConfigStore.ts: Manages the state of panel access based on user profiles.
// - @profileStore.ts: Stores user profile information and manages user sessions.
// - @hasAccessToPanel.ts: Utility functions to check access rights for specific panels.
// - @chat-header.tsx: Component that utilizes profile information to display relevant header panels.
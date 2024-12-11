// LayoutContext.tsx
'use client'
import React, { createContext, useContext, useState, useEffect } from 'react';
import { getLayoutProps } from '../config/panelLayoutConfig';
import { UserProfile } from '../config/profileConfig';

type LayoutContextType = {
  layoutProps: ReturnType<typeof getLayoutProps>;
  updateLayout: (params: {
    profile: UserProfile;
    showChatHistory: boolean;
    showChatArtifacts: boolean;
    showChatProcessor: boolean;
    showChatControls: boolean;
  }) => void;
};

const LayoutContext = createContext<LayoutContextType | undefined>(undefined);

export const LayoutProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [layoutProps, setLayoutProps] = useState(() => getLayoutProps(
    {} as UserProfile, 0, false, false, false, false
  ));

  const updateLayout = (params: {
    profile: UserProfile;
    showChatHistory: boolean;
    showChatArtifacts: boolean;
    showChatProcessor: boolean;
    showChatControls: boolean;
  }) => {
    const newLayoutProps = getLayoutProps(
      params.profile,
      [params.showChatArtifacts, params.showChatProcessor, params.showChatControls].filter(Boolean).length,
      params.showChatHistory,
      params.showChatArtifacts,
      params.showChatProcessor,
      params.showChatControls
    );
    setLayoutProps(newLayoutProps);
  };

  return (
    <LayoutContext.Provider value={{ layoutProps, updateLayout }}>
      {children}
    </LayoutContext.Provider>
  );
};

export const useLayout = () => {
  const context = useContext(LayoutContext);
  if (context === undefined) {
    throw new Error('useLayout must be used within a LayoutProvider');
  }
  return context;
};
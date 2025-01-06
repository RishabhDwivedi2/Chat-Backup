// src/components/custom/layout/panel-layout.tsx

'use client';

import { useEffect, useState } from 'react';
import { ThemeProvider } from 'next-themes';
import useProfileStore from '@/store/profileStore';
import useDynamicProfileConfigStore from '@/store/dynamicProfileConfigStore';
import FullPageLoader from '@/components/custom/loaders/full-page-loader';
import PanelRenderer from '@/components/custom/chat-bot/panel-renderer';
import { ErrorBoundary } from 'react-error-boundary';
import { removeThemeClasses } from '@/config/themeConfig';
import { usePathname, useRouter } from 'next/navigation';

const useLoadingState = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const { setIsHydrated, isHydrated } = useProfileStore();
  const { migrateConfigs } = useDynamicProfileConfigStore();

  useEffect(() => {
    const prepare = async () => {
      try {
        await new Promise(resolve => setTimeout(resolve, 0));
        await migrateConfigs();
        await new Promise(resolve => setTimeout(resolve, 1000));
        setIsHydrated(true);
        setIsLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('An unknown error occurred'));
        setIsLoading(false);
      }
    };

    prepare();
  }, [setIsHydrated, migrateConfigs]);

  return { isLoading, error, isHydrated };
};

const ErrorFallback = ({ error, resetErrorBoundary }: { error: Error; resetErrorBoundary: () => void }) => (
  <div role="alert">
    <p>Something went wrong:</p>
    <pre>{error.message}</pre>
    <button onClick={resetErrorBoundary}>Try again</button>
  </div>
);

const ThemedPanelRenderer = () => {
  const { color, mode } = useProfileStore();

  useEffect(() => {
    const themeRoot = document.getElementById('theme-root');
    if (!themeRoot) return;

    removeThemeClasses(themeRoot);
    themeRoot.classList.add(color.toLowerCase());
    themeRoot.classList.add(mode.toLowerCase());
  }, [color, mode]);

  return (
    <div id="theme-root">
      <ThemeProvider attribute="class" defaultTheme={mode}>
        <PanelRenderer />
      </ThemeProvider>
    </div>
  );
};

interface PanelLayoutProps {
    chatId?: string;
  }
  
  export default function PanelLayout({ chatId }: PanelLayoutProps) {
    const { profile } = useProfileStore();
    const { isLoading, error, isHydrated } = useLoadingState();
    const router = useRouter();
    const pathname = usePathname();
  
    useEffect(() => {
      if (!profile) {
        router.replace('/');
      }
    }, [profile, router]);
  
    useEffect(() => {
      if (chatId) {
        localStorage.setItem('currentConversationId', chatId);
      } else if (pathname === '/new') {
        localStorage.removeItem('currentConversationId');
      }
    }, [chatId, pathname]);
  
    if (!profile) return null;
  
    if (isLoading || !isHydrated) {
      return <FullPageLoader />;
    }
  
    if (error) {
      return <ErrorFallback error={error} resetErrorBoundary={() => window.location.reload()} />;
    }
  
    return (
      <ErrorBoundary
        FallbackComponent={ErrorFallback}
        onReset={() => window.location.reload()}
      >
        <ThemedPanelRenderer />
      </ErrorBoundary>
    );
  }
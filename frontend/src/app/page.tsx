// src/app/page.tsx

'use client';

import { useEffect, useState } from 'react';
import { ThemeProvider } from 'next-themes';
import useProfileStore from '@/store/profileStore';
import useDynamicProfileConfigStore from '@/store/dynamicProfileConfigStore';
import FullPageLoader from '@/components/custom/loaders/full-page-loader';
import PanelRenderer from '@/components/custom/chat-bot/panel-renderer';
import { Welcome } from '@/components/custom/chat-bot/welcome';
import { ErrorBoundary } from 'react-error-boundary';
import { removeThemeClasses } from '@/config/themeConfig';

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

export default function Home() {
  const { profile } = useProfileStore();
  const { isLoading, error, isHydrated } = useLoadingState();

  if (isLoading || !isHydrated) {
    return <FullPageLoader />;
  }

  if (error) {
    return <ErrorFallback error={error} resetErrorBoundary={() => window.location.reload()} />;
  }

  if (!profile) {
    return <Welcome />;
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
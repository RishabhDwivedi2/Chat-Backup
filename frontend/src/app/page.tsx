// src/app/page.tsx

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import useProfileStore from '@/store/profileStore';
import { Welcome } from '@/components/custom/chat-bot/welcome';

export default function RootPage() {
  const router = useRouter();
  const { profile } = useProfileStore();

  useEffect(() => {
    if (profile) {
      const currentConversationId = localStorage.getItem('currentConversationId');
      if (currentConversationId) {
        router.replace(`/chat/${currentConversationId}`);
      } else {
        router.replace('/new');
      }
    }
  }, [profile, router]);

  return profile ? null : <Welcome />;
}
// src/app/(pages)/chat/[id]/page.tsx

'use client';

import PanelLayout from '@/components/custom/layout/panel-layout';
import { useParams } from 'next/navigation';

export default function ChatPage() {
  const params = useParams();
  const chatId = params?.id as string;
  
  return <PanelLayout chatId={chatId} />;
}
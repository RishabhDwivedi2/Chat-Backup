// ChatHistory.tsx
import React, { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useRouter } from 'next/navigation';
import ChatsTab from '@/components/custom/chat-controller/chat-data/chat-tab';
import ArtifactsTab from '@/components/custom/chat-controller/chat-data/artifacts-tab';
import AttachmentsTab from '@/components/custom/chat-controller/chat-data/attachments-tab';
import AnalysisTab from '@/components/custom/chat-controller/chat-data/analysis-tab';

interface ChatHistoryProps {
    chatId: string;
    onClose: () => void;
}

const ChatHistory: React.FC<ChatHistoryProps> = ({ chatId, onClose }) => {
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const timer = setTimeout(() => {
            setIsLoading(false);
        }, 1500);

        return () => clearTimeout(timer);
    }, [chatId]);

    const handleCloseClick = () => {
        onClose();
        if (chatId) {
            router.replace('/chat-controller');
        }
    }

    return (
        <div className="chat-controls rounded-lg border bg-[hsl(var(--background))] h-[calc(100vh-100px)] flex flex-col shadow-lg overflow-hidden">
            <div className="sticky top-0 z-10 bg-[hsl(var(--background))] pt-3 px-6 pb-3 flex justify-between items-center">
                <h2 className="text-lg font-medium">{chatId || 'Chat History'}</h2>
                <Button
                    variant="ghost"
                    className="p-2 text-gray-400 hover:text-black"
                    onClick={handleCloseClick}
                >
                    <X className="w-5 h-5" />
                </Button>
            </div>
            <Tabs defaultValue="chats" className="flex-grow flex flex-col px-6">
                <TabsList className="grid w-full grid-cols-4 rounded-sm">
                    <TabsTrigger value="chats">Chats</TabsTrigger>
                    <TabsTrigger value="artifacts">Artifacts</TabsTrigger>
                    <TabsTrigger value="attachments">Attachments</TabsTrigger>
                    <TabsTrigger value="analysis">Analysis</TabsTrigger>
                </TabsList>
                <div className="flex-grow overflow-hidden" style={{ scrollbarGutter: 'stable' }}>
                    <TabsContent value="chats" className="h-full">
                        <ChatsTab isLoading={isLoading} />
                    </TabsContent>
                    <TabsContent value="artifacts" className="mt-4">
                        <ArtifactsTab />
                    </TabsContent>
                    <TabsContent value="attachments" className="mt-4">
                        <AttachmentsTab />
                    </TabsContent>
                    <TabsContent value="analysis" className="mt-4 space-y-4 h-full">
                        <AnalysisTab />
                    </TabsContent>
                </div>
            </Tabs>
        </div>
    );
}

export default ChatHistory;
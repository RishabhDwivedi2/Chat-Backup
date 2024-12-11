// File: src/components/custom/chat-bot/chat-history.tsx

import React, { useState, useEffect } from 'react';
import { ArrowLeft, ChevronLeft, PanelLeftClose, MessageSquarePlus, MessageSquareText, DoorOpen, Minimize2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import AnimatedShinyText from '@/components/magicui/animated-shiny-text';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { motion, AnimatePresence } from 'framer-motion';
import { format } from 'date-fns';

interface ChatCollection {
    id: number;
    collection_name: string;
    created_at: string;
    conversation_count: number;
}

interface ChatHistoryProps {
    className?: string;
    onClose: () => void;
    isMobile: boolean;
    isCoreRunning: boolean;
    onBackToWebsite: () => void;
    isVisible: boolean;
    onConversationSelect: (messages: any[]) => void;
}

export default function ChatHistory({
    className,
    onClose,
    isMobile,
    isCoreRunning,
    onBackToWebsite,
    isVisible,
    onConversationSelect
}: ChatHistoryProps) {
    const [collections, setCollections] = useState<ChatCollection[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleNewChat = () => {
        localStorage.removeItem('currentConversationId');

        const resetEvent = new CustomEvent('resetChat', {
            detail: { trigger: 'newChat' }
        });
        window.dispatchEvent(resetEvent);

        onClose();
    };

    useEffect(() => {
        const fetchCollections = async () => {
            if (!isVisible) return;

            setIsLoading(true);
            setError(null);

            try {
                const token = localStorage.getItem('token');
                const response = await fetch('/api/chat-history', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch chat history');
                }

                const data = await response.json();
                setCollections(data);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to load chat history');
                console.error('Error loading collections:', err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchCollections();
    }, [isVisible]);

    const handleChatClick = async (chatId: number) => {
        try {
            setIsLoading(true);
            const token = localStorage.getItem('token');

            localStorage.setItem('currentConversationId', chatId.toString());

            const response = await fetch(`/api/conversations/${chatId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Failed to fetch conversation');
            }

            const data = await response.json();

            const formattedMessages = data.messages.map((msg: any) => ({
                role: msg.role,
                content: msg.content,
                ...(msg.attachments?.length > 0 && { files: msg.attachments }),
                ...(msg.artifacts?.length > 0 && {
                    component: msg.artifacts[0].component_type,
                    data: msg.artifacts[0].data,
                    artifactId: msg.artifacts[0].id
                })
            }));

            onConversationSelect(formattedMessages);

            if (isMobile) {
                onClose();
            }

        } catch (error) {
            console.error('Error loading conversation:', error);
            setError('Failed to load conversation');
        } finally {
            setIsLoading(false);
        }
    };

    const groupCollectionsByDate = (collections: ChatCollection[]) => {
        return collections.reduce((groups, chat) => {
            const date = new Date(chat.created_at);
            const today = new Date();
            const yesterday = new Date(today);
            yesterday.setDate(yesterday.getDate() - 1);

            let dateGroup;
            if (date.toDateString() === today.toDateString()) {
                dateGroup = 'Today';
            } else if (date.toDateString() === yesterday.toDateString()) {
                dateGroup = 'Yesterday';
            } else if (date > new Date(today.setDate(today.getDate() - 7))) {
                dateGroup = format(date, 'EEEE');
            } else {
                dateGroup = 'Older';
            }

            if (!groups[dateGroup]) {
                groups[dateGroup] = [];
            }
            groups[dateGroup].push(chat);
            return groups;
        }, {} as Record<string, ChatCollection[]>);
    };

    const mobileVariants = {
        hidden: { x: '-100%' },
        visible: { x: 0 },
        exit: { x: '-100%' }
    };

    const desktopVariants = {
        hidden: { x: '-100%' },
        visible: { x: 0 },
        exit: { x: '-100%' }
    };

    const groupedCollections = groupCollectionsByDate(collections);

    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    className={`
                ${isMobile
                            ? 'fixed top-0 left-0 bottom-0 w-[80%] max-w-[300px] z-50'
                            : 'h-full border z-40 flex flex-col'}
                bg-background text-foreground
                ${className}
              `}
                    variants={isMobile ? mobileVariants : desktopVariants}
                    initial="hidden"
                    animate="visible"
                    exit="exit"
                    transition={{ duration: 0.3 }}
                >
                    <div className={`h-full flex flex-col ${isMobile ? 'border-r border-border' : ''}`}>
                        <div className="header p-2 flex items-center justify-between border-b border-border">
                            <div className='flex items-center'>
                                <AnimatedShinyText className="ml-2 flex-grow transition ease-out hover:text-muted-foreground cursor-pointer">
                                    <span className="text-xl font-bold">✨ Chat.</span>
                                </AnimatedShinyText>
                            </div>

                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Button
                                        variant="ghost"
                                        onClick={onClose}
                                        className="p-2 text-muted-foreground hover:text-foreground ml-auto"
                                    >
                                        <PanelLeftClose className="w-5 h-5" />
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent>
                                    <span>Close panel</span>
                                </TooltipContent>
                            </Tooltip>
                        </div>

                        <div className="flex-grow overflow-auto p-2">
                            <ul className="space-y-2">
                                <li
                                    className="text-muted-foreground flex items-center py-2 px-3 hover:bg-accent hover:text-accent-foreground rounded-md cursor-pointer"
                                    onClick={handleNewChat}
                                >
                                    <MessageSquarePlus className="w-4 h-4 mr-3" />
                                    <span className="text-[16px] font-medium">Start new chat</span>
                                </li>
                            </ul>

                            {isLoading ? (
                                <div className="flex justify-center items-center mt-4">
                                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                                </div>
                            ) : error ? (
                                <div className="text-destructive text-center mt-4 p-2">
                                    {error}
                                </div>
                            ) : collections.length === 0 ? (
                                <div className="text-muted-foreground text-center mt-4 p-2">
                                    No chat history found
                                </div>
                            ) : (
                                Object.entries(groupedCollections).map(([date, chats]) => (
                                    <div key={date} className="mt-4">
                                        <h2 className="text-xs font-semibold text-muted-foreground mb-2">{date}</h2>
                                        <ul className="space-y-1">
                                            {chats.map((chat) => (
                                                <li
                                                    key={chat.id}
                                                    onClick={() => handleChatClick(chat.id)}
                                                    className="flex items-center py-2 px-3 hover:bg-accent hover:text-accent-foreground rounded-md cursor-pointer group"
                                                >
                                                    <MessageSquareText className="w-4 h-4 mr-3 flex-shrink-0" />
                                                    <span className="text-sm line-clamp-2 break-words">
                                                        {chat.collection_name}
                                                    </span>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                ))
                            )}
                        </div>

                        <div className="p-2 border-t border-border">
                            <div className="flex items-center py-2 px-3 hover:bg-accent hover:text-accent-foreground rounded-md cursor-pointer">
                                <div className="w-6 h-6 bg-primary text-primary-foreground rounded-full flex items-center justify-center mr-2">
                                    <span className="text-xs font-bold">RD</span>
                                </div>
                                <span className="text-sm">rishabh.dwivedi@deltabots.ai</span>
                            </div>
                        </div>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
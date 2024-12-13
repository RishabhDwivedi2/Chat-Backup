// File: src/components/custom/chat-bot/chat-history.tsx

import React, { useState, useEffect, useCallback } from 'react';
import { ArrowLeft, ChevronLeft, PanelLeftClose, MessageSquarePlus, MessageSquareText, DoorOpen, Minimize2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import AnimatedShinyText from '@/components/magicui/animated-shiny-text';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { motion, AnimatePresence } from 'framer-motion';
import { differenceInDays, format, isSameDay, isYesterday } from 'date-fns';

interface Conversation {
    id: number;
    title: string;
    last_message_at: string;
    message_count: number;
}

interface ChatCollection {
    id: number;
    collection_name: string;
    created_at: string;
    conversation_count: number;
    conversations: Conversation[];
}

interface ChatHistoryProps {
    className?: string;
    onClose: () => void;
    isMobile: boolean;
    isCoreRunning: boolean;
    onBackToWebsite: () => void;
    isVisible: boolean;
    onConversationSelect: (messages: any[], conversationId: number) => void; 
    collections: ChatCollection[];
    isLoading: boolean;
    error: string | null;
    onNewChat: () => void;
    onRefreshHistory: () => Promise<void>; 
    activeConversationId?: number | null;
}

export default function ChatHistory({
    className,
    onClose,
    isMobile,
    isCoreRunning,
    onBackToWebsite,
    isVisible,
    onConversationSelect,
    collections,
    isLoading,
    error,
    onNewChat,
    activeConversationId,
}: ChatHistoryProps) {
    const [selectedChatId, setSelectedChatId] = useState<number | null>(activeConversationId || null);

    useEffect(() => {
        const storedConversationId = localStorage.getItem('currentConversationId');
        if (storedConversationId) {
            const conversationId = parseInt(storedConversationId);
            setSelectedChatId(conversationId);
            loadConversation(conversationId);
        }
    }, []);

    useEffect(() => {
        if (activeConversationId) {
            setSelectedChatId(activeConversationId);
        }
    }, [activeConversationId]);

    const handleChatClick = async (collection: ChatCollection) => {
        if (!collection.conversations || collection.conversations.length === 0) {
            console.error('No conversations found in collection');
            return;
        }

        const conversationId = collection.conversations[0].id;
        setSelectedChatId(conversationId);
        localStorage.setItem('currentConversationId', conversationId.toString());
        await loadConversation(conversationId);
    };

    const loadConversation = async (conversationId: number) => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`/api/conversations/${conversationId}`, {
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

            onConversationSelect(formattedMessages, conversationId);
        } catch (error) {
            console.error('Error loading conversation:', error);
        }
    };

    const handleNewChat = () => {
        setSelectedChatId(null);
        localStorage.removeItem('currentConversationId');
        onNewChat();
    };

    const groupCollectionsByDate = (collections: ChatCollection[]) => {
        const today = new Date();
        
        return collections.reduce((groups, chat) => {
            const date = new Date(chat.created_at);
            
            if (isSameDay(date, today)) {
                if (!groups['Today']) groups['Today'] = [];
                groups['Today'].push(chat);
            }
            else if (isYesterday(date)) {
                if (!groups['Yesterday']) groups['Yesterday'] = [];
                groups['Yesterday'].push(chat);
            }
            else if (differenceInDays(today, date) <= 30) {
                if (!groups['Last 30 Days']) groups['Last 30 Days'] = [];
                groups['Last 30 Days'].push(chat);
            }
            else {
                if (!groups['Older']) groups['Older'] = [];
                groups['Older'].push(chat);
            }
            
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
                    ${isMobile ? 'fixed top-0 left-0 bottom-0 w-[80%] max-w-[300px] z-50' : 'h-full border z-40 flex flex-col'}
                    bg-background text-foreground 
                    ${!isVisible ? 'hidden' : ''}
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
                                    className={`text-muted-foreground flex items-center py-2 px-3 hover:bg-accent hover:text-accent-foreground rounded-md cursor-pointer ${!selectedChatId ? 'bg-accent text-accent-foreground' : ''}`}
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
                                Object.entries(groupCollectionsByDate(collections)).map(([date, collections]) => (
                                    <div key={date} className="mt-4">
                                        <h2 className="text-xs font-semibold text-muted-foreground mb-2">{date}</h2>
                                        <ul className="space-y-1">
                                            {collections.map((collection) => {
                                                const isSelected = collection.conversations?.[0]?.id === selectedChatId;
                                                return (
                                                    <li
                                                        key={collection.id}
                                                        onClick={() => handleChatClick(collection)}
                                                        className={`flex items-center py-2 px-3 hover:bg-accent hover:text-accent-foreground rounded-md cursor-pointer group
                                                            ${isSelected ? 'bg-accent text-accent-foreground' : ''}`}
                                                    >
                                                        <MessageSquareText className="w-4 h-4 mr-3 flex-shrink-0" />
                                                        <span className="text-sm line-clamp-2 break-words">
                                                            {collection.collection_name}
                                                        </span>
                                                    </li>
                                                );
                                            })}
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
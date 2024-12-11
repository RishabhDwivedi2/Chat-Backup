'use client'

import React, { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { motion, AnimatePresence } from 'framer-motion';
import { SpokeSpinner } from '@/components/ui/spinner';
import { RefreshCw, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { useRouter, useSearchParams } from 'next/navigation';
import { BorderBeam } from '@/components/magicui/border-beam';

interface ChatCardProps {
    id: string;
    chatId: string;
    lastMessageTime: string;
    onClick: (id: string) => void;
}

interface InitialChatsProps {
    onChatClick: (chatId: string) => void;
}

interface TimeZoneSectionProps {
    title: string;
    chats: Omit<ChatCardProps, 'onClick'>[];
    onChatClick: (chatId: string) => void;
}

const ChatCard: React.FC<ChatCardProps> = ({ chatId, lastMessageTime, onClick }) => {
    const router = useRouter();
    const searchParams = useSearchParams();

    const handleClick = (id: string) => {
        onClick(id);
        const params = new URLSearchParams(searchParams);
        params.set('chatId', id);
        router.push(`/chat-controller?${params.toString()}`, { scroll: false });
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.98 }}
            transition={{ type: "spring", stiffness: 400, damping: 17 }}
        >
            <Card className="mb-2 cursor-pointer" onClick={() => handleClick(chatId)}>
                <CardContent className="flex items-center gap-4 p-4">
                    <div className="p-2 bg-blue-500 rounded-sm">
                        <span className="text-white font-bold">{chatId.charAt(5).toUpperCase() + chatId.charAt(6)}</span>
                    </div>
                    <div>
                        <div className="text-sm font-medium">
                            {chatId}
                        </div>
                        <p className="text-xs">{lastMessageTime}</p>
                    </div>
                </CardContent>
            </Card>
        </motion.div>
    );
};

const TimeZoneSection: React.FC<TimeZoneSectionProps> = ({ title, chats, onChatClick }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-6"
    >
        <h4 className="text-sm font-medium mb-2">{title}</h4>
        <AnimatePresence>
            {chats.map((chat, index) => (
                <motion.div
                    key={chat.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ delay: index * 0.1 }}
                >
                    <ChatCard {...chat} onClick={onChatClick} />
                </motion.div>
            ))}
        </AnimatePresence>
    </motion.div>
);

const InitialChats: React.FC<InitialChatsProps> = ({ onChatClick }) => {
    const [todayChats, setTodayChats] = useState<ChatCardProps[]>([]);
    const [yesterdayChats, setYesterdayChats] = useState<ChatCardProps[]>([]);
    const [olderChats, setOlderChats] = useState<ChatCardProps[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isSearchLoading, setIsSearchLoading] = useState(false);
    const [totalChats, setTotalChats] = useState(0);
    const [searchTerm, setSearchTerm] = useState('');
    const [filteredChats, setFilteredChats] = useState<ChatCardProps[]>([]);
    const [noResultFound, setNoResultFound] = useState(false);
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [isSearching, setIsSearching] = useState(false);
    const router = useRouter();
    const searchParams = useSearchParams();
    const chatId = searchParams.get('chatId');

    const fetchChatIds = async () => {
        setIsLoading(true);
        try {
            const response = await fetch('/api/chat-controller/chat-ids');
            const chatIds: string[] = await response.json();

            const fetchedTodayChats: ChatCardProps[] = [];
            const fetchedYesterdayChats: ChatCardProps[] = [];
            const fetchedOlderChats: ChatCardProps[] = [];

            chatIds.forEach((chatId, index) => {
                const chatData: ChatCardProps = {
                    id: `chat-${index}-${chatId}`,
                    chatId,
                    lastMessageTime: `${index + 1}h ago`,
                    onClick: onChatClick
                };

                if (index < 3) {
                    fetchedTodayChats.push(chatData);
                } else if (index >= 3 && index < 6) {
                    chatData.lastMessageTime = '1d ago';
                    fetchedYesterdayChats.push(chatData);
                } else {
                    chatData.lastMessageTime = '2d ago';
                    fetchedOlderChats.push(chatData);
                }
            });

            setTodayChats(fetchedTodayChats);
            setYesterdayChats(fetchedYesterdayChats);
            setOlderChats(fetchedOlderChats);
            setTotalChats(chatIds.length);
            setFilteredChats(fetchedTodayChats.concat(fetchedYesterdayChats, fetchedOlderChats));
            setIsSearching(false);
        } catch (error) {
            console.error('Error fetching chat IDs:', error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (chatId) {
            router.replace('/chat-controller');
        }
        fetchChatIds();
    }, []);

    const handleSearch = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setIsSearchLoading(true);
        setNoResultFound(false);
        await new Promise((resolve) => setTimeout(resolve, 1000));
        const searchResult = filteredChats.filter(chat =>
            chat.chatId.toLowerCase().includes(searchTerm.toLowerCase())
        );
        setFilteredChats(searchResult);
        setIsSearchLoading(false);
        setIsDialogOpen(false);
        setIsSearching(true);
        if (searchResult.length === 0) {
            setNoResultFound(true);
        }
    };

    const handleReload = () => {
        setIsSearching(false);
        fetchChatIds();
    };

    return (
        <AnimatePresence mode="wait">
            {isLoading ? (
                <motion.div
                    key="loader"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex justify-center items-center h-[calc(100vh-100px)]"
                >
                    <div className="flex flex-col">
                        <SpokeSpinner size='xl' color='black' />
                        <p className="text-var(--loader) text-xl mt-4">Loading...</p>
                    </div>
                </motion.div>
            ) : (
                <motion.div
                    key="content"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.5 }}
                    className="chat-controls rounded-lg border bg-[hsl(var(--background))] h-[calc(100vh-100px)] flex flex-col shadow-lg overflow-hidden"
                >
                    <div className="sticky top-0 z-10 bg-[hsl(var(--background))] pt-3 px-6 pb-3 flex justify-between items-center">

                        <div>
                            <h2 className="text-lg font-medium">All Chats</h2>
                            <p className="text-sm text-gray-500">Total chats: {totalChats}</p>
                        </div>
                        <div className="flex gap-2">
                            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                                <DialogTrigger asChild>
                                    <Button variant="ghost" size="icon">
                                        <Search className="w-5 h-5 text-gray-500 hover:text-gray-700" />
                                    </Button>
                                </DialogTrigger>
                                <DialogContent className='font-poppins'>
                                    <DialogHeader>
                                        <DialogTitle>Search Chat</DialogTitle>
                                    </DialogHeader>
                                    <form onSubmit={handleSearch}>
                                        <Input
                                            type="text"
                                            placeholder="Search by chat ID"
                                            value={searchTerm}
                                            onChange={e => setSearchTerm(e.target.value)}
                                        />
                                    </form>
                                    {isSearchLoading && (
                                        <div className="flex justify-center items-center h-20">
                                            <SpokeSpinner size="md" color="zinc" />
                                        </div>
                                    )}
                                </DialogContent>
                            </Dialog>

                            {/* Reload Icon */}
                            <Button variant="ghost" size="icon" onClick={handleReload} aria-label="Reload chats">
                                <RefreshCw className="w-5 h-5 text-gray-500 hover:text-gray-700" />
                            </Button>
                        </div>
                    </div>
                    <div className="flex-grow overflow-y-auto px-6 pb-6" style={{ scrollbarGutter: 'stable' }}>
                        <div className="pr-4">
                            {isSearching ? (
                                <TimeZoneSection title="Search Results" chats={filteredChats} onChatClick={onChatClick} />
                            ) : (
                                <>
                                    <TimeZoneSection title="Today" chats={todayChats} onChatClick={onChatClick} />
                                    <TimeZoneSection title="Yesterday" chats={yesterdayChats} onChatClick={onChatClick} />
                                    {olderChats.length > 0 && (
                                        <TimeZoneSection title="Earlier" chats={olderChats} onChatClick={onChatClick} />
                                    )}
                                </>
                            )}

                            {noResultFound && (
                                <p className="text-center text-gray-500 mt-10">No results found.</p>
                            )}
                        </div>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

export default InitialChats;

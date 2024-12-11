'use client'

import React, { useState, useEffect } from 'react';
import ChatHistory from "@/components/custom/chat-controller/chat-history";
import InitialChats from "@/components/custom/chat-controller/initial-chats";

export default function Manager() {
    const [selectedChatId, setSelectedChatId] = useState<string | null>(null);

    const handleChatClick = (chatId: string) => {
        setSelectedChatId(chatId);
    };

    const handleCloseChatHistory = () => {
        setSelectedChatId(null);
    };

    useEffect(() => {
        const root = document.documentElement;
        if (selectedChatId) {
            root.style.setProperty('--initial-chats-width', '35%');
            root.style.setProperty('--chat-history-width', '60%');
        } else {
            root.style.setProperty('--initial-chats-width', '40%');
            root.style.setProperty('--chat-history-width', '0%');
        }
    }, [selectedChatId]);

    return (
        <div className="manager-container flex justify-center items-start h-screen pt-[20px] px-4 pb-4">
            <div
                className="transition-all duration-300 ease-in-out h-full"
                style={{ width: 'var(--initial-chats-width)' }}
            >
                <InitialChats onChatClick={handleChatClick} />
            </div>
            {selectedChatId && (
                <div
                    className="transition-all duration-300 ease-in-out ml-4 h-full"
                    style={{ width: 'var(--chat-history-width)' }}
                >
                    <ChatHistory chatId={selectedChatId} onClose={handleCloseChatHistory} />
                </div>
            )}
        </div>
    );
}
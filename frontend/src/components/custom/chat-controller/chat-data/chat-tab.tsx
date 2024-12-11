// ChatsTab.tsx
import React, { useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { SpokeSpinner } from "@/components/ui/spinner";

interface ChatsTabProps {
    isLoading: boolean;
}

const ChatsTab: React.FC<ChatsTabProps> = ({ isLoading }) => {
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!isLoading && messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [isLoading]);

    const messages = [
        { type: 'assistant', content: 'Hello! How can I assist you today?' },
        { type: 'user', content: 'I have a question about my account balance.' },
        { type: 'assistant', content: "Certainly! I'd be happy to help you with that. Could you please provide me with your account number?" },
        { type: 'user', content: 'My account number is 1234567890.' },
        { type: 'assistant', content: "Thank you for providing that information. I've looked up your account, and your current balance is $5,000. Is there anything else you'd like to know about your account?" },
        { type: 'user', content: 'What is the minimum payment due on my credit card?' },
        { type: 'assistant', content: "I apologize for the confusion. Let me check that information for you. Your minimum payment due on your credit card is $150. The payment is due on the 15th of this month. Is there anything else you'd like to know about your credit card or any other accounts?" },
    ];

    return (
        <div className="h-[83%] mt-4 mb-4 px-6 overflow-y-auto" style={{ scrollbarGutter: 'stable' }}>
            <AnimatePresence>
                {isLoading ? (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="flex justify-center items-center h-full"
                    >
                        <SpokeSpinner />
                    </motion.div>
                ) : (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="space-y-4 pb-4"
                    >
                        {messages.map((message, index) => (
                            <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`max-w-[70%] p-3 rounded-lg ${message.type === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-100'}`}>
                                    {message.content}
                                </div>
                            </div>
                        ))}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

export default ChatsTab;
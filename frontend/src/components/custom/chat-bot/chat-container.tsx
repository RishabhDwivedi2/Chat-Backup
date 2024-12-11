// src/components/custom/chat-bot/chat-container.tsx

'use client';

import React, { useEffect, useRef, useState } from "react";
import { useProcessorStore } from "@/store/processorStore";
import { ChatArea } from "./chat-area";
import { ChatForm } from "./chat-form";
import { UserProfile } from "@/config/profileConfig";
import { ChatFontStyle } from './panel-renderer';
import usePanelConfigStore from "@/store/accessPanelConfigStore";
import { ToastAction } from "@/components/ui/toast";
import { useToast } from "@/hooks/use-toast";
import { formatFileSize } from "@/utils/fileHandlers";

interface UploadedFile extends File {
    documentId?: number;
    downloadUrl: string;
    storagePath: string;
    fileDetails?: any;
}

interface Message {
    id: string;
    role: string;
    content: string;
    files?: UploadedFile[];
    component?: "Table" | "Chart" | "Card" | "Text";
    data?: any;
    artifactId?: string;
    summary?: string;
    timestamp?: string;
    attachments?: any[];
    metadata?: any;
}

interface Artifact {
    id: string;
    title: string;
    component: string;
    data: any;
    version: number;
    isLoading?: boolean;
}

interface ChatContainerProps {
    messages: Message[];
    attachedFiles: UploadedFile[];
    setAttachedFiles: React.Dispatch<React.SetStateAction<UploadedFile[]>>;
    setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
    fileInputRef: React.RefObject<HTMLInputElement>;
    showChatControls: boolean;
    chatIdRef: React.MutableRefObject<string | null>;
    chatbotContainerRef: React.RefObject<HTMLDivElement>;
    showChatArtifacts: boolean;
    className: string;
    setShowChatArtifacts: React.Dispatch<React.SetStateAction<boolean>>;
    setArtifactsData: React.Dispatch<React.SetStateAction<any>>;
    onDrop: (e: React.DragEvent<HTMLDivElement>) => void;
    profile: UserProfile;
    onArtifactsUpdate: (artifacts: Artifact[]) => void;
    chatFontStyle: ChatFontStyle;
    onClose: () => void;
    isChatArtifactsActive: React.Dispatch<React.SetStateAction<boolean>>;
    isMobile: boolean;
    onNewArtifact: (artifact: Artifact) => void;
}


export const ChatContainer: React.FC<ChatContainerProps> = ({
    messages,
    attachedFiles,
    setAttachedFiles,
    setMessages,
    fileInputRef,
    showChatControls,
    chatIdRef,
    chatbotContainerRef,
    showChatArtifacts,
    className,
    setShowChatArtifacts,
    setArtifactsData,
    onDrop,
    profile,
    onArtifactsUpdate,
    chatFontStyle,
    onClose,
    isChatArtifactsActive,
    isMobile,
    onNewArtifact,
}) => {
    const { toast } = useToast();
    const [inputMessage, setInputMessage] = useState("");
    const [textareaHeight, setTextareaHeight] = useState(50);
    const [isSendDisabled, setIsSendDisabled] = useState(true);
    const maxTextareaHeight = 200;
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const [artifacts, setArtifacts] = useState<Artifact[]>([]);

    const { addAnalysis, updateStep, setAgent1Response, setAgent2Response } = useProcessorStore();

    const { panelConfig } = usePanelConfigStore();

    useEffect(() => {
        const handleChatReset = (event: CustomEvent) => {
            // Reset messages to initial state
            // setMessages([
            //     { role: "assistant", content: "Hello! How can I assist you today?" }
            // ]);
            
            // Clear attached files
            setAttachedFiles([]);
            
            // Reset input if any
            setInputMessage("");
            resetTextareaHeight();
            
            // Reset any artifacts if they exist
            setArtifacts([]);
        };

        // Add event listener with type assertion
        window.addEventListener('resetChat', handleChatReset as EventListener);

        // Cleanup
        return () => {
            window.removeEventListener('resetChat', handleChatReset as EventListener);
        };
    }, [setMessages, setAttachedFiles]); // Include all necessary dependencies


    const adjustTextareaHeight = (textarea: HTMLTextAreaElement) => {
        textarea.style.height = "auto";
        const newHeight = textarea.scrollHeight;

        if (newHeight > textarea.offsetHeight && newHeight <= maxTextareaHeight) {
            setTextareaHeight(newHeight);
            textarea.style.height = `${newHeight}px`;
        } else if (newHeight > maxTextareaHeight) {
            setTextareaHeight(maxTextareaHeight);
            textarea.style.height = `${maxTextareaHeight}px`;
        }

        if (textarea.value === "") {
            resetTextareaHeight();
        }
    };

    const resetTextareaHeight = () => {
        setTextareaHeight(50);
        setInputMessage("");
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInputMessage(e.target.value);
        adjustTextareaHeight(e.target);
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        if (chatbotContainerRef.current) {
            chatbotContainerRef.current.scrollTo({
                top: chatbotContainerRef.current.scrollHeight,
                behavior: 'smooth',
            });
        }
    };

    useEffect(() => {
        const handleStorageChange = (e: StorageEvent) => {
            if (e.key === 'currentConversationId' && e.newValue === null) {
                setMessages([]);
                setAttachedFiles([]);
                setInputMessage("");
            }
        };

        window.addEventListener('storage', handleStorageChange);
        return () => window.removeEventListener('storage', handleStorageChange);
    }, []);

    const showTypingEffect = async (text: string, baseTypingSpeed = 1) => {
        let typedMessage = '';
        let index = 0;

        return new Promise<void>((resolve) => {
            const typingStep = () => {
                if (index < text.length) {
                    typedMessage += text[index];
                    index++;

                    setMessages((prevMessages) =>
                        prevMessages.map((msg, i, arr) =>
                            i === arr.length - 1 && msg.role === "assistant"
                                ? { ...msg, content: typedMessage }
                                : msg
                        )
                    );
                    scrollToBottom();
                    setTimeout(() => requestAnimationFrame(typingStep), baseTypingSpeed);
                } else {
                    resolve();
                }
            };

            typingStep();
        });
    };

    const handleSendMessage = async (e: React.FormEvent, files: UploadedFile[]) => {
        e.preventDefault();
        if (inputMessage.trim()) {

            console.group('Chat Message Submission');
            console.log('Input Message:', inputMessage);
            console.log('Files received by handleSendMessage:', files);
            console.log('Files type:', Object.prototype.toString.call(files));
            console.log('Is array?', Array.isArray(files));
            console.log('Files length:', files?.length);


            if (files && Array.isArray(files) && files.length > 0) {
                console.group('Attached Files');
                files.forEach((file, index) => {  // Use the files parameter here
                    console.log(`File ${index + 1}:`, {
                        name: file.name,
                        type: file.type,
                        size: formatFileSize(file.size),
                        downloadUrl: file.downloadUrl,
                        storagePath: file.storagePath,
                        fileDetails: file.fileDetails
                    });
                });
                console.groupEnd();
            }

            const newUserMessage = { 
                id: `msg-${Date.now()}`,
                role: "user", 
                content: inputMessage, 
                files: files 
            };
            setMessages((prevMessages) => [...prevMessages, newUserMessage]);

            setInputMessage("");
            setAttachedFiles([]);

            const pendingAssistantMessage = { 
                id: `msg-${Date.now()}-pending`,
                role: "assistant_pending", 
                content: "Assistant is analyzing..." 
            };
            setMessages((prevMessages) => [...prevMessages, pendingAssistantMessage]);
            scrollToBottom();

            const analysisId = `analysis-${Date.now()}`;

            addAnalysis({
                id: analysisId,
                title: `Analysis for "${inputMessage.substring(0, 20)}..."`,
                subtext: 'Processing user input',
                steps: [
                    { name: 'Processing Request', duration: '-', status: 'pending' },
                    { name: 'Generating Response', duration: '-', status: 'pending' },
                ],
                agent1Response: null,
                agent2Response: null,
            });

            try {
                updateStep(analysisId, 0, 'inProgress');
                const processingStartTime = performance.now();

                const token = localStorage.getItem('token')?.replace(/bearer/gi, '').trim() || '';
                const authHeader = token ? `Bearer ${token}` : '';

                const currentConversationId = localStorage.getItem('currentConversationId');

                const formData = new FormData();
                formData.append('prompt', inputMessage);
                formData.append('max_tokens', '100');
                formData.append('temperature', '0.7');

                if (currentConversationId) {
                    console.log("Continuing conversation:", currentConversationId);
                    formData.append('conversation_id', currentConversationId);
                } else {
                    console.log("Starting new conversation");
                }

                if (files && files.length > 0) {
                    console.group('Processing files for FormData:');
                    
                    files.forEach((file) => {
                        const attachmentData = {
                            name: file.name,
                            type: file.type,
                            size: file.size,
                            storagePath: file.storagePath,
                            downloadUrl: file.downloadUrl,
                            fileDetails: file.fileDetails
                        };
                
                        console.log('Adding attachment to FormData:', attachmentData);
                        formData.append('attachments', JSON.stringify(attachmentData));
                    });
                    
                    console.groupEnd();
                }
        
                // Log final FormData contents
                console.group('Final FormData Contents:');
                for (const [key, value] of formData.entries()) {
                    if (value instanceof File) {
                        console.log(`${key}:`, {
                            name: value.name,
                            type: value.type,
                            size: value.size
                        });
                    } else {
                        console.log(`${key}:`, value);
                    }
                }
                console.groupEnd();

                const chatResponse = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Authorization': authHeader
                    },
                    body: formData
                });

                if (!chatResponse.ok) {
                    throw new Error(`Chat API failed: ${chatResponse.status} ${chatResponse.statusText}`);
                }

                const processingEndTime = performance.now();
                updateStep(analysisId, 0, 'completed', `${(processingEndTime - processingStartTime).toFixed(2)}ms`);

                const chatData = await chatResponse.json();
                const parsedResponse = JSON.parse(chatData.response);

                console.log("Response Conversation ID:", parsedResponse.message.conversation_id);

                if (parsedResponse.message.conversation_id) {
                    localStorage.setItem('currentConversationId', String(parsedResponse.message.conversation_id));
                }

                const structuredResponse = parsedResponse.message.structured_response;
                console.log("Structured Response:", structuredResponse);

                setMessages((prevMessages) =>
                    prevMessages.map((msg) =>
                        msg.role === "assistant_pending"
                            ? {
                                id: `msg-${chatData.message_id || Date.now()}`,
                                role: "assistant",
                                content: "",
                                messageId: chatData.message_id
                            }
                            : msg
                    )
                );

                updateStep(analysisId, 1, 'inProgress');
                const responseStartTime = performance.now();

                await showTypingEffect(structuredResponse.content);

                const loadingArtifactId = `artifact-${Date.now()}`;
                const canShowArtifacts = panelConfig[profile as keyof typeof panelConfig].panels.includes("ChatArtifacts");

                if (structuredResponse.has_artifact) {
                    if (canShowArtifacts) {
                        const loadingArtifact = {
                            id: loadingArtifactId,
                            title: structuredResponse.data?.title || "Loading Artifact",
                            component: structuredResponse.component_type,
                            data: null,
                            version: 1,
                            isLoading: true,
                        };

                        setArtifacts(prevArtifacts => [...prevArtifacts, loadingArtifact]);
                        setMessages(prevMessages => [
                            ...prevMessages,
                            { id: `msg-${Date.now()}-artifact`, role: 'artifact', artifactId: loadingArtifactId, content: '' }
                        ]);
                        scrollToBottom();

                        const newArtifact = {
                            id: structuredResponse.artifact_id,
                            component: structuredResponse.component_type,
                            sub_type: structuredResponse.sub_type,
                            data: structuredResponse.data,
                            title: structuredResponse.data?.title || "Generated Visualization",
                            version: 1,
                            isLoading: false
                        };

                        if (canShowArtifacts) {
                            setArtifacts(prevArtifacts =>
                                prevArtifacts.map(artifact =>
                                    artifact.isLoading ? newArtifact : artifact
                                )
                            );
                            setMessages(prevMessages =>
                                prevMessages.map(msg =>
                                    msg.role === 'artifact' && msg.artifactId === loadingArtifactId
                                        ? {
                                            ...msg,
                                            artifactId: newArtifact.id,
                                            component: structuredResponse.component_type,
                                            data: structuredResponse.data,
                                            summary: structuredResponse.summary
                                        }
                                        : msg
                                )
                            );
                        } else {
                            setMessages((prevMessages) =>
                                prevMessages.map((msg, index) =>
                                    index === prevMessages.length - 1 && msg.role === "assistant"
                                        ? {
                                            ...msg,
                                            component: structuredResponse.component_type,
                                            data: structuredResponse.data,
                                            summary: structuredResponse.summary
                                        }
                                        : msg
                                )
                            );
                            setArtifacts(prevArtifacts => [...prevArtifacts, newArtifact]);
                        }

                        const updatedArtifacts = artifacts.filter(a => !a.isLoading).concat(newArtifact);
                        onArtifactsUpdate(updatedArtifacts);

                        if (canShowArtifacts) {
                            onClose();
                            onNewArtifact(newArtifact);
                            setArtifactsData(newArtifact);
                        }
                    }
                }

                const responseEndTime = performance.now();
                updateStep(analysisId, 1, 'completed', `${(responseEndTime - responseStartTime).toFixed(2)}ms`);

            } catch (error) {
                console.error("Error processing message:", error);
                setMessages((prevMessages) => [
                    ...prevMessages.filter((msg) => msg.role !== "assistant_pending"),
                    { id: `msg-${Date.now()}-error`, role: "assistant", content: "Something went wrong. Please try again." },
                ]);
                updateStep(analysisId, 0, 'inProgress');
                updateStep(analysisId, 1, 'inProgress');
            } finally {
                scrollToBottom();
                textareaRef.current?.focus();
            }
        }
    };

    useEffect(() => {
        setIsSendDisabled(inputMessage.trim() === "");
    }, [inputMessage]);

    const handleArtifactClick = (artifactId: string) => {
        console.log("Artifact clicked:", artifactId);
    };

    const panelList = panelConfig[profile as keyof typeof panelConfig].panels;

    const containerClassName = `chat-container relative flex h-full min-h-[50vh] p-0 flex-col rounded-xl ${isMobile ? 'w-full' : className
        }`;

    return (
        <div className={containerClassName}>
            <ChatArea
                messages={messages}
                artifacts={artifacts}
                handleArtifactClick={handleArtifactClick}
                profile={profile}
                chatFontStyle={chatFontStyle}
            />

            {panelList.includes("ChatControls") && (
                <ChatForm
                    inputMessage={inputMessage}
                    setInputMessage={setInputMessage}
                    handleSendMessage={handleSendMessage}
                    handleInputChange={handleInputChange}
                    isSendDisabled={isSendDisabled}
                />
            )}
        </div>
    );
};

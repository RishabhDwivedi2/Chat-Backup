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
import { Message, FileAttachment } from '@/types/chat';

interface UploadedFile extends File {
    documentId?: number;
    downloadUrl: string;
    storagePath: string;
    fileDetails?: any;
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
    onRefreshHistory: () => Promise<void>;
    onSetActiveConversation: (conversationId: number) => void;
    onConversationPlatformChange?: (isPlatformChanged: boolean, platform?: string) => void;
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
    onRefreshHistory,
    onSetActiveConversation,
    onConversationPlatformChange
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
            setMessages([]);
            setAttachedFiles([]);
            setInputMessage("");
            resetTextareaHeight();
            setArtifacts([]);
        };

        const handleStorageChange = (e: StorageEvent) => {
            if (e.key === 'currentConversationId' && e.newValue === null) {
                setMessages([]);
                setAttachedFiles([]);
                setInputMessage("");
            }
        };

        window.addEventListener('resetChat', handleChatReset as EventListener);
        window.addEventListener('storage', handleStorageChange);

        return () => {
            window.removeEventListener('resetChat', handleChatReset as EventListener);
            window.removeEventListener('storage', handleStorageChange);
        };
    }, []);

    useEffect(() => {
        const handlePlatformChange = (event: CustomEvent) => {
            const { isPlatformChanged, platform, previousPlatform } = event.detail;
            
            if (isPlatformChanged && onConversationPlatformChange) {
                onConversationPlatformChange(isPlatformChanged, platform);
            }
        };

        window.addEventListener('conversationPlatformChange', handlePlatformChange as EventListener);
        
        return () => {
            window.removeEventListener('conversationPlatformChange', handlePlatformChange as EventListener);
        };
    }, [onConversationPlatformChange]);

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

    const populateAssistantMessage = async (text: string) => {
        setMessages((prevMessages) =>
            prevMessages.map((msg, i, arr) =>
                i === arr.length - 1 && msg.role === "assistant"
                    ? { ...msg, content: text } // Ensure this is a valid Message type
                    : msg
            )
        );
        scrollToBottom();
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
                files.forEach((file, index) => {
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
    
            const newUserMessage: Message = { // Ensure this is a valid Message type
                id: `msg-${Date.now()}`,
                role: "user",
                content: inputMessage,
                files: files
            };
            setMessages((prevMessages) => [...prevMessages, newUserMessage]);    
    
            setInputMessage("");
            setAttachedFiles([]);
    
            const pendingAssistantMessage: Message = { // Ensure this is a valid Message type
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
                const isNewConversation = !currentConversationId;
    
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
                console.log("Platform Changed:", parsedResponse.message.this_request_makes_platform_changed);

                if (parsedResponse.message.this_request_makes_platform_changed) {
                    toast({
                        title: "Platform Updated",
                        className: "font-poppins",
                        description: "This conversation has been updated from GMAIL to WEB",
                        variant: "default",
                        duration: 5000,
                        action: <ToastAction altText="Okay">Okay</ToastAction>
                    });
                }                
    
                if (parsedResponse.message.conversation_id) {
                    const newConversationId = String(parsedResponse.message.conversation_id);
                    localStorage.setItem('currentConversationId', newConversationId);
    
                    if (!currentConversationId) {
                        await onRefreshHistory();
                        onSetActiveConversation(parseInt(newConversationId));
                    }
                }
    
                const structuredResponse = parsedResponse.message.structured_response;
                console.log("Structured Response:", structuredResponse);
    
                // Create the assistant message with potential artifact information
                const assistantMessage: Message = { // Ensure this is a valid Message type
                    id: `msg-${chatData.message_id || Date.now()}`,
                    role: "assistant",
                    content: "",
                    messageId: chatData.message_id,
                    isNew: true
                };
    
                // If there's an artifact, add the artifact information to the message
                if (structuredResponse.has_artifact) {
                    // Get title from metadata
                    const artifactTitle = structuredResponse.metadata?.title ||
                                        structuredResponse.data?.title ||
                                        "Generated Visualization";
    
                    const artifactInfo = {
                        artifactId: structuredResponse.artifact_id,
                        component: structuredResponse.component_type,
                        data: {
                            ...structuredResponse.data,
                            title: artifactTitle // Ensure title is in data object
                        },
                        artifactTitle: artifactTitle,
                        summary: structuredResponse.summary,
                        metadata: structuredResponse.metadata // Pass through all metadata
                    };
                    Object.assign(assistantMessage, artifactInfo);
                }
    
                // Update messages state with the new assistant message
                setMessages(prevMessages => 
                    prevMessages.map(msg => 
                        msg.role === "assistant_pending" 
                            ? assistantMessage 
                            : msg
                    )
                );
    
                updateStep(analysisId, 1, 'inProgress');
                const responseStartTime = performance.now();
    
                await populateAssistantMessage(structuredResponse.content);
    
                const canShowArtifacts = panelConfig[profile as keyof typeof panelConfig].panels.includes("ChatArtifacts");
    
                if (structuredResponse.has_artifact) {
                    // Get title from metadata for the artifact
                    const artifactTitle = structuredResponse.metadata?.title ||
                                        structuredResponse.data?.title ||
                                        "Generated Visualization";
    
                    const newArtifact = {
                        id: structuredResponse.artifact_id,
                        title: artifactTitle,
                        component: structuredResponse.component_type,
                        sub_type: structuredResponse.sub_type,
                        data: {
                            ...structuredResponse.data,
                            title: artifactTitle,
                            metadata: structuredResponse.metadata // Include metadata in data
                        },
                        version: 1,
                        isLoading: false
                    };
    
                    setArtifacts(prevArtifacts => [...prevArtifacts, newArtifact]);
                    onArtifactsUpdate([...artifacts, newArtifact]);
    
                    if (canShowArtifacts) {
                        onClose();
                        onNewArtifact(newArtifact);
                        setArtifactsData({
                            component: structuredResponse.component_type,
                            sub_type: structuredResponse.sub_type,
                            data: {
                                ...structuredResponse.data,
                                title: artifactTitle,
                                style: structuredResponse.style,
                                metadata: structuredResponse.metadata
                            }
                        });
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
                setMessages={setMessages}
                artifacts={artifacts}
                handleArtifactClick={handleArtifactClick}
                profile={profile}
                chatFontStyle={chatFontStyle}
                onShowChatArtifacts={setShowChatArtifacts}
                setArtifactsData={setArtifactsData}
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

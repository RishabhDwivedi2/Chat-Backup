// File: src/components/custom/chat-bot/panel-renderer.tsx

import dynamic from "next/dynamic";
import { useState, useRef, useEffect, useMemo, useCallback } from "react";
import { TooltipProvider } from "@/components/ui/tooltip";
import ChatControls from "./chat-controls";
import { ChatHeader } from "./chat-header";
import { ChatContainer } from "./chat-container";
import ChatArtifacts from "./chat-artifacts";
import ChatHistory from "./chat-history";
import ChatProcessor from "./chat-processor";
import { useToast } from "@/hooks/use-toast";
import { ToastAction } from "@/components/ui/toast";
import { AnimatePresence, motion } from "framer-motion";
import useProfileStore from "@/store/profileStore";
import usePanelConfigStore from "@/store/accessPanelConfigStore";
import { getLayoutProps } from "@/config/panelLayoutConfig";
import { UserProfile } from '@/config/profileConfig';
import MoreOptions from "./mobile-view/more-options";
import { useRouter } from "next/navigation";
import useDynamicProfileConfigStore from "@/store/dynamicProfileConfigStore";
import { Message, ChatCollection } from "@/types/chat";

const AnimatedGridPattern = dynamic(
    () => import("@/components/magicui/animated-grid-pattern"),
    { ssr: false }
);

interface Artifact {
    id: string;
    title: string;
    component: string;
    data: any;
    version: number;
}

interface UploadedFile extends File {
    documentId?: number;
    downloadUrl: string;
    storagePath: string;
}

const generateChatId = () => {
    const characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
    let chatId = "";
    for (let i = 0; i < 7; i++) {
        chatId += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    return chatId;
};

export type ChatFontStyle = 'Default' | 'Match System' | 'Dyslexic friendly';

type DrawerOption = 'Chat Controls' | 'Artifacts' | 'Processor';

const PanelRenderer: React.FC = () => {
    const router = useRouter();

    const { profile, userName, isHydrated, setIsHydrated } = useProfileStore();
    const { panelConfig } = usePanelConfigStore();

    const [messages, setMessages] = useState<Message[]>([]);
    const [attachedFiles, setAttachedFiles] = useState<UploadedFile[]>([]);
    const fileInputRef = useRef<HTMLInputElement | null>(null);
    const chatIdRef = useRef<string | null>(null);
    const chatbotContainerRef = useRef<HTMLDivElement | null>(null);

    const { toast } = useToast();

    const [showChatControls, setShowChatControls] = useState(false);
    const [showChatArtifacts, setShowChatArtifacts] = useState(false);
    const [showChatHistory, setShowChatHistory] = useState(false);
    const [showChatProcessor, setShowChatProcessor] = useState(false);
    const [showAnimatedText, setShowAnimatedText] = useState(true);

    const [isChatHistoryActive, setIsChatHistoryActive] = useState(false);
    const [isChatProcessorActive, setIsChatProcessorActive] = useState(false);
    const [isChatControlsActive, setIsChatControlsActive] = useState(false);
    const [isChatArtifactsActive, setIsChatArtifactsActive] = useState(false);

    const [artifactsData, setArtifactsData] = useState<{ component: string; data: any } | null>(null);
    const [artifacts, setArtifacts] = useState<Artifact[]>([]);

    const [chatFontStyle, setChatFontStyle] = useState<ChatFontStyle>('Default');

    const [isMobile, setIsMobile] = useState(false);

    const [isDrawerOpen, setIsDrawerOpen] = useState(false);
    const [lastGeneratedArtifact, setLastGeneratedArtifact] = useState<Artifact | null>(null);


    useEffect(() => {
        const handleResize = () => {
            setIsMobile(window.innerWidth < 600);
        };
        handleResize();
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    const { migrateConfigs } = useDynamicProfileConfigStore();

    useEffect(() => {
        migrateConfigs();
    }, [migrateConfigs]);


    const layoutProps = useMemo(() => {
        return getLayoutProps(
            profile as UserProfile,
            [showChatArtifacts, showChatProcessor, showChatControls].filter(Boolean).length,
            showChatHistory,
            showChatArtifacts,
            showChatProcessor,
            showChatControls
        );
    }, [profile, showChatArtifacts, showChatProcessor, showChatControls, showChatHistory]);

    const togglePanel = (panel: 'ChatControls' | 'ChatArtifacts' | 'ChatProcessor' | 'ChatHistory') => {
        if (isMobile && panel !== 'ChatHistory') {
            setIsDrawerOpen(true);
            return;
        }

        const config = panelConfig[profile as keyof typeof panelConfig];

        const panelState = {
            ChatControls: { show: showChatControls, setShow: setShowChatControls, setActive: setIsChatControlsActive },
            ChatArtifacts: { show: showChatArtifacts, setShow: setShowChatArtifacts, setActive: setIsChatArtifactsActive },
            ChatProcessor: { show: showChatProcessor, setShow: setShowChatProcessor, setActive: setIsChatProcessorActive },
            ChatHistory: { show: showChatHistory, setShow: setShowChatHistory, setActive: setIsChatHistoryActive },
        };

        const currentPanels = Object.keys(panelState)
            .filter(key => panelState[key as keyof typeof panelState].show)
            .map(key => key as string);

        const visiblePanelsCount = currentPanels.length + 1;
        const maxPanels = config.maxPanels;

        if (config.exclusivePanels) {
            config.exclusivePanels.forEach(exclusiveGroup => {
                if (exclusiveGroup.includes(panel)) {
                    exclusiveGroup.forEach(exclusivePanel => {
                        if (exclusivePanel !== panel && panelState[exclusivePanel as keyof typeof panelState].show) {
                            panelState[exclusivePanel as keyof typeof panelState].setShow(false);
                        }
                    });
                }
            });
        }

        if (!panelState[panel].show && visiblePanelsCount >= maxPanels) {
            if (showChatControls) {
                setShowChatControls(false);
                setIsChatControlsActive(false);
            } else {
                toast({
                    title: "Maximum Panels Reached",
                    description: `You have reached the maximum number of panels (${maxPanels}). Close another panel to open ${panel}.`,
                    variant: "destructive",
                    className: "font-poppins",
                    action: <ToastAction altText="Okay">Okay</ToastAction>,
                });
                return;
            }
        }

        const newPanelState = !panelState[panel].show;
        panelState[panel].setShow(newPanelState);
        panelState[panel].setActive(newPanelState);

        if (panel === 'ChatHistory') {
            setShowAnimatedText(!newPanelState);
        }

        if (config.exclusivePanels && panel === 'ChatArtifacts' && !newPanelState) {
            const artifactsExclusiveGroup = config.exclusivePanels.find(group => group.includes('ChatArtifacts'));
            if (artifactsExclusiveGroup && artifactsExclusiveGroup.includes('ChatControls')) {
                setShowChatControls(true);
                setIsChatControlsActive(true);
            }
        }
    };

    const closeChatControls = () => {
        setShowChatControls(false);
        setIsChatControlsActive(false);
    };

    const handleFileDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        const files = Array.from(e.dataTransfer.files) as UploadedFile[];
        setAttachedFiles([...attachedFiles, ...files]);
    };

    useEffect(() => {
        if (!chatIdRef.current) {
            const newChatId = generateChatId();
            chatIdRef.current = newChatId;
        }
    }, []);

    const handleArtifactsUpdate = (updatedArtifacts: Artifact[]) => {
        setArtifacts(updatedArtifacts);
    };

    const handleFontStyleChange = (newStyle: ChatFontStyle) => {
        setChatFontStyle(newStyle);
    };

    const handleNewArtifact = (newArtifact: Artifact) => {
        setArtifacts(prevArtifacts => [...prevArtifacts, newArtifact]);
        setLastGeneratedArtifact(newArtifact);
        if (isMobile) {
            setIsDrawerOpen(true);
        } else {
            setIsChatArtifactsActive(true);
            setShowChatArtifacts(true);
            setArtifactsData({ component: newArtifact.component, data: newArtifact.data });
        }
    };

    const [isCoreRunning, setIsCoreRunning] = useState(false);

    useEffect(() => {
        fetch('http://localhost:3000/api/health')
            .then((res) => {
                if (res.ok) {
                    setIsCoreRunning(true);
                } else {
                    setIsCoreRunning(false);
                }
            })
            .catch(() => {
                setIsCoreRunning(false);
            });
    }, []);

    const handleBackToWebsite = () => {
        router.push("http://localhost:3000");
    };



    // Chat History



    const [collections, setCollections] = useState<ChatCollection[]>([]);
    const [isHistoryLoading, setIsHistoryLoading] = useState(false);
    const [historyError, setHistoryError] = useState<string | null>(null);
    const [activeConversationId, setActiveConversationId] = useState<number | null>(null);

    useEffect(() => {
        const handleStorageChange = (e: StorageEvent) => {
            if (e.key === 'currentConversationId' && e.newValue === null) {
                const resetEvent = new CustomEvent('resetChat', {
                    detail: { trigger: 'storage' }
                });
                window.dispatchEvent(resetEvent);
            }
        };

        const handleChatReset = () => {
            setShowChatArtifacts(false);
            setArtifactsData(null);
            setLastGeneratedArtifact(null);
        };

        window.addEventListener('storage', handleStorageChange);
        window.addEventListener('resetChat', handleChatReset);

        return () => {
            window.removeEventListener('storage', handleStorageChange);
            window.removeEventListener('resetChat', handleChatReset);
        };
    }, []);

    const handleConversationSelect = (messages: any[], conversationId: number) => {
        setMessages(messages);
        setActiveConversationId(conversationId);

        setAttachedFiles([]);
        setArtifacts(messages.reduce((acc: Artifact[], msg: any) => {
            if (msg.component && msg.data && msg.artifactId) {
                acc.push({
                    id: msg.artifactId,
                    title: msg.data.title || 'Generated Visualization',
                    component: msg.component,
                    data: msg.data,
                    version: 1
                });
            }
            return acc;
        }, []));
    };

    const fetchChatHistory = useCallback(async () => {
        setIsHistoryLoading(true);
        setHistoryError(null);

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
            setHistoryError(err instanceof Error ? err.message : 'Failed to load chat history');
            console.error('Error loading collections:', err);
        } finally {
            setIsHistoryLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchChatHistory();
    }, []);

    const handleNewChat = useCallback(() => {
        setMessages([]);
        setAttachedFiles([]);
        setArtifacts([]);
        localStorage.removeItem('currentConversationId');

        const resetEvent = new CustomEvent('resetChat', {
            detail: { trigger: 'newChat' }
        });
        window.dispatchEvent(resetEvent);

        fetchChatHistory();
    }, [fetchChatHistory]);


    const handlePlatformChange = (isPlatformChanged: boolean, platform?: string) => {
        if (isPlatformChanged && platform) {
            toast({
                title: "Platform Changed",
                description: `This conversation will no longer continue via ${platform}`,
                variant: "default",
                className: "font-poppins",
                duration: 5000,
                action: <ToastAction altText="Okay">Okay</ToastAction>,
            });
        }
    };

    return (
        <TooltipProvider>
            <div className="flex h-screen w-full font-poppins">
                <AnimatedGridPattern
                    numSquares={30}
                    maxOpacity={0.1}
                    duration={3}
                    repeatDelay={1}
                    className="absolute inset-0 [mask-image:radial-gradient(500px_circle_at_center,white,transparent)]"
                />

                <div className="flex w-full h-screen">
                    <AnimatePresence>
                        {showChatHistory && isMobile && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                transition={{ duration: 0.2 }}
                                className="fixed inset-0 bg-black bg-opacity-50 z-40"
                                onClick={() => togglePanel('ChatHistory')}
                            />
                        )}
                    </AnimatePresence>

                    <div className={`${!showChatHistory ? 'hidden' : ''}`}>
                        <ChatHistory
                            onClose={() => togglePanel('ChatHistory')}
                            className={isMobile ? "w-full" : "w-80"}
                            isMobile={isMobile}
                            isCoreRunning={isCoreRunning}
                            onBackToWebsite={handleBackToWebsite}
                            isVisible={showChatHistory}
                            collections={collections}
                            isLoading={isHistoryLoading}
                            error={historyError}
                            onNewChat={handleNewChat}
                            activeConversationId={activeConversationId}
                            onConversationSelect={handleConversationSelect}
                            onRefreshHistory={fetchChatHistory}
                            onShowChatArtifacts={setShowChatArtifacts}
                            setArtifactsData={setArtifactsData}
                        />
                    </div>

                    <div className="flex flex-col flex-1">
                        <ChatHeader
                            toggleChatControls={() => togglePanel('ChatControls')}
                            closeChatControls={closeChatControls}
                            toggleChatHistory={() => togglePanel('ChatHistory')}
                            toggleChatArtifacts={() => togglePanel('ChatArtifacts')}
                            toggleChatProcessor={() => togglePanel('ChatProcessor')}
                            showAnimatedText={showAnimatedText}
                            isChatHistoryActive={isChatHistoryActive}
                            isChatArtifactsActive={isChatArtifactsActive}
                            isChatProcessorActive={isChatProcessorActive}
                            isChatControlsActive={isChatControlsActive}
                            username={userName || "Guest"}
                            profile={profile as UserProfile}
                            onMoreDetails={() => setIsDrawerOpen(true)}
                            isCoreRunning={isCoreRunning}
                            onBackToWebsite={handleBackToWebsite}
                        />

                        <main
                            className={`chatbot-container flex flex-1 gap-4 overflow-y-auto overflow-x-hidden p-4 lg:flex-row ${layoutProps.justifyContent}`}
                            ref={chatbotContainerRef}
                        >
                            {profile && panelConfig[profile as keyof typeof panelConfig]?.panels.includes("ChatContainer") && (
                                <ChatContainer
                                    chatbotContainerRef={chatbotContainerRef}
                                    messages={messages}
                                    setMessages={setMessages}
                                    attachedFiles={attachedFiles}
                                    setAttachedFiles={setAttachedFiles}
                                    fileInputRef={fileInputRef}
                                    showChatControls={showChatControls}
                                    chatIdRef={chatIdRef}
                                    showChatArtifacts={showChatArtifacts}
                                    setShowChatArtifacts={setShowChatArtifacts}
                                    setArtifactsData={setArtifactsData}
                                    onDrop={handleFileDrop}
                                    profile={profile as UserProfile}
                                    onArtifactsUpdate={handleArtifactsUpdate}
                                    chatFontStyle={chatFontStyle}
                                    onClose={closeChatControls}
                                    isChatArtifactsActive={setIsChatArtifactsActive}
                                    className={`flex-1 ${isMobile ? 'w-full' : layoutProps.chatContainerWidth}`}
                                    isMobile={isMobile}
                                    onNewArtifact={handleNewArtifact}
                                    onRefreshHistory={fetchChatHistory}
                                    onSetActiveConversation={setActiveConversationId}
                                    onConversationPlatformChange={handlePlatformChange}
                                />
                            )}

                            {showChatArtifacts && !isMobile && (
                                <motion.div
                                    initial={{ opacity: 0, x: 50 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: 50 }}
                                    transition={{ duration: 0.5 }}
                                    className={`sticky top-0 h-full bg-background ${layoutProps.chatArtifactsWidth > 'w-[50%]' ? 'w-[50%] max-w-[50%]' : layoutProps.chatArtifactsWidth}`}
                                    style={{ maxHeight: '100vh', overflowY: 'auto' }}
                                >
                                    <ChatArtifacts
                                        onClose={() => togglePanel('ChatArtifacts')}
                                        className={`lg:flex-shrink-0 ${layoutProps.chatArtifactsWidth}`}
                                        artifactsData={artifactsData || { component: "Text", data: {} }}
                                        onShowChatControls={() => togglePanel('ChatControls')}
                                        profile={profile as UserProfile}
                                    />
                                </motion.div>
                            )}

                            {showChatProcessor && !isMobile && (
                                <motion.div
                                    initial={{ opacity: 0, x: 50 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: 50 }}
                                    transition={{ duration: 0.5 }}
                                    className={`sticky top-0 h-full bg-background ${layoutProps.chatProcessorWidth > 'w-[50%]' ? 'w-[50%] max-w-[50%]' : layoutProps.chatProcessorWidth}`}
                                    style={{ maxHeight: '100vh', overflowY: 'auto' }}
                                >
                                    <ChatProcessor
                                        className={`lg:flex-shrink-0 ${layoutProps.chatProcessorWidth}`}
                                        onClose={() => togglePanel('ChatProcessor')}
                                    />
                                </motion.div>
                            )}

                            {showChatControls && !isMobile && (
                                <motion.div
                                    initial={{ opacity: 0, x: 50 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: 50 }}
                                    transition={{ duration: 0.5 }}
                                    className={`sticky top-0 h-full bg-background ${layoutProps.chatControlsWidth > 'w-[35%]' ? 'w-[35%] max-w-[35%]' : layoutProps.chatControlsWidth} flex-shrink flex-grow-0`}
                                    style={{ maxHeight: '100vh', overflowY: 'auto' }}
                                >
                                    <ChatControls
                                        chats={[]}
                                        onClose={closeChatControls}
                                        onShowArtifacts={() => togglePanel('ChatArtifacts')}
                                        className={`lg:flex-shrink-0 ${layoutProps.chatControlsWidth}`}
                                        profile={profile as UserProfile}
                                        artifacts={artifacts}
                                        messages={messages}
                                        chatFontStyle={chatFontStyle}
                                        onFontStyleChange={handleFontStyleChange}
                                    />
                                </motion.div>
                            )}
                        </main>
                    </div>
                </div>
                {/* Mobile View */}
                <MoreOptions
                    isOpen={isDrawerOpen}
                    onOpenChange={setIsDrawerOpen}
                    defaultOption={lastGeneratedArtifact ? 'Artifacts' : 'Chat Controls'}
                    profile={profile as UserProfile}
                    artifacts={artifacts}
                    lastGeneratedArtifact={lastGeneratedArtifact}
                    messages={messages}
                    chatFontStyle={chatFontStyle}
                    onFontStyleChange={handleFontStyleChange}
                />
            </div>
        </TooltipProvider>
    );
};

export default dynamic(() => Promise.resolve(PanelRenderer), { ssr: false });
// File: src/components/custom/chat-bot/chat-controls.tsx

import React, { useEffect, useState } from 'react';
import { X, FileText, CodeXml, Settings2, ChevronsRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent } from '@/components/ui/card';
import { UserProfile } from "@/config/profileConfig";
import { ChatFontStyle } from './panel-renderer';
import { hasAccessToPanel, hasMinimumProfileLevel } from '@/utils/hasAccessToPanel';
import { Message, FileAttachment } from '@/types/chat';

type Chat = {
    id: string;
    title: string;
};

interface Artifact {
    id: string;
    title: string;
    component: string;
    data: any;
    version: number;
}

interface ChatControlsProps {
    chats: any[];
    onClose: () => void;
    onShowArtifacts: () => void;
    className?: string;
    profile: UserProfile;
    artifacts: Artifact[];
    messages: Message[];
    chatFontStyle: ChatFontStyle;
    onFontStyleChange: (style: ChatFontStyle) => void;
}

const ChatControls = ({ onClose, onShowArtifacts, className, profile, artifacts: initialArtifacts, messages, chatFontStyle, onFontStyleChange }: ChatControlsProps) => {
    const [attachments, setAttachments] = useState<FileAttachment[]>([]);
    const [artifacts, setArtifacts] = useState<Artifact[]>(initialArtifacts);
    const [isLoading, setIsLoading] = useState(false);

    const fetchArtifacts = async () => {
        try {
            setIsLoading(true);
            const currentConversationId = localStorage.getItem('currentConversationId');
            
            if (!currentConversationId) {
                setArtifacts(initialArtifacts);
                return;
            }
    
            // Log for debugging
            console.log('Fetching artifacts for conversation:', currentConversationId);
    
            const token = localStorage.getItem('token');
            if (!token) {
                console.error('No token found');
                return;
            }
    
            const response = await fetch(`/api/artifact-history/${currentConversationId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
    
            if (!response.ok) {
                const errorData = await response.json();
                console.error('Failed to fetch artifacts:', errorData);
                throw new Error('Failed to fetch artifacts');
            }
    
            const data = await response.json();
            
            // Log the response data
            console.log('Received artifacts data:', data);
    
            // Transform the API response into the Artifact type
            const formattedArtifacts = data.map((artifact: any) => ({
                id: artifact.id.toString(),
                title: artifact.title || artifact.metadata?.title || 'Generated Artifact',
                component: artifact.component_type,
                data: {
                    ...artifact.data,
                    title: artifact.title || artifact.metadata?.title,
                    metadata: artifact.metadata
                },
                version: artifact.version || 1
            }));
    
            setArtifacts(formattedArtifacts);
        } catch (error) {
            console.error('Error fetching artifacts:', error);
            // Keep the existing artifacts on error
            setArtifacts(initialArtifacts);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchArtifacts();
    }, [initialArtifacts]); // Fetch when initialArtifacts changes

    useEffect(() => {
        const allAttachments = messages.flatMap(message => message.files || []);
        setAttachments(allAttachments);
    }, [messages]);

    const canAccessArtifacts = hasMinimumProfileLevel(profile, 2);

    const handleArtifactClick = (artifactId: string) => {
        if (canAccessArtifacts) {
            onShowArtifacts();
        } else {
            console.log("Artifact clicked, but ChatArtifacts not available for this profile");
        }
    };

    const hasContent = artifacts.length > 0 || attachments.length > 0;

    return (
        <div className={`h-full flex flex-col rounded-lg border border-border bg-background overflow-hidden sticky top-0`}>
            <div className="flex items-center justify-between p-4 border-b border-border">
                <div className="flex items-center gap-2">
                    <div className="p-2 bg-blue-100 rounded-full">
                        <Settings2 className="w-5 h-5 text-blue-500" />
                    </div>
                    <h2 className="text-md font-medium text-foreground">Chat Controls</h2>
                </div>
                <Button
                    variant="ghost"
                    onClick={onClose}
                    className="p-2 text-muted-foreground hover:text-foreground"
                >
                    <ChevronsRight className="w-5 h-5" />
                </Button>
            </div>

            <div className="flex-grow overflow-y-auto overflow-x-hidden relative px-2 py-2">
                {!hasContent ? (
                    <div className="flex flex-col items-center justify-center border border-border my-4 rounded-md text-center p-4 text-muted-foreground">
                        <h3 className="text-md font-medium mb-2">No content added yet</h3>
                        <p className="text-sm">
                            Add images, PDFs, docs, spreadsheets, and more to summarize,
                            analyze, and query content with Claude.
                        </p>
                    </div>
                ) : (
                    <>
                        {artifacts.length > 0 && (
                            <div className="w-full mb-6 mt-1">
                                <h4 className="text-sm font-small mb-2 text-foreground">
                                    Artifacts {isLoading && <span className="text-xs">(Loading...)</span>}
                                </h4>
                                {artifacts.map((artifact) => (
                                    <Card key={artifact.id} onClick={() => handleArtifactClick(artifact.id)} className="mb-2">
                                        <CardContent className="flex items-center gap-4 p-4 cursor-pointer">
                                            <div className="p-2 bg-secondary rounded">
                                                <CodeXml className="w-6 h-6 text-secondary-foreground" />
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium text-foreground">{artifact.title}</p>
                                                <p className="text-xs text-muted-foreground">
                                                    {canAccessArtifacts ? 'Click to open component' : 'Artifact view not available'} • {artifact.version} version(s)
                                                </p>
                                            </div>
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        )}

                        {attachments.length > 0 && (
                            <div className="w-full mb-6">
                                <h4 className="text-sm font-small mb-2 text-foreground">Attachments</h4>
                                {attachments.map((file, index) => (
                                    <Card key={index} className="mb-2">
                                        <CardContent className="flex items-center gap-4 p-4 cursor-pointer">
                                            <div className="p-2 bg-primary rounded">
                                                <FileText className="w-6 h-6 text-primary-foreground" />
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium text-foreground">{file.name}</p>
                                                <p className="text-xs text-muted-foreground">
                                                    {file.size ? `${(file.size / 1024).toFixed(2)} KB` : 'Size unknown'}
                                                </p>
                                            </div>
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        )}
                    </>
                )}

                <div className="w-full mb-6">
                    <h4 className="text-sm font-small mb-2 text-foreground">Chat styles</h4>
                    <Card>
                        <CardContent className="flex items-center justify-between p-4">
                            <span className="text-sm text-foreground">Aa</span>
                            <Select value={chatFontStyle} onValueChange={(value: ChatFontStyle) => onFontStyleChange(value)}>
                                <SelectTrigger className="w-[180px] border bg-background text-foreground">
                                    <SelectValue placeholder="Font" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="Default">Default</SelectItem>
                                    <SelectItem value="Match System">Match System</SelectItem>
                                    <SelectItem value="Dyslexic friendly">Dyslexic friendly</SelectItem>
                                </SelectContent>
                            </Select>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
};

export default ChatControls;
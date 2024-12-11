// File: src/components/custom/chat-bot/chat-area.tsx

import React, { useState } from 'react';
import { Brain, FileText, CodeXml, X } from 'lucide-react';
import DynamicComponent from './dynamic-component';
import { Card, CardContent } from '@/components/ui/card';
import { SpokeSpinner } from '@/components/ui/spinner';
import { ChatFontStyle } from './panel-renderer';
import { hasMinimumProfileLevel } from '@/utils/hasAccessToPanel';
import { UserProfile } from '@/config/profileConfig';
import { Dialog, DialogContent, DialogClose } from "@/components/ui/dialog";

interface Message {
    role: string;
    content: string;
    files?: File[];
    component?: "Table" | "Chart" | "Card" | "Text";
    data?: any;
    artifactId?: string;
    summary?: string;
}

interface Artifact {
    id: string;
    title: string;
    component: string;
    data: any;
    version: number;
    isLoading?: boolean;
}

interface ChatAreaProps {
    messages: Message[];
    artifacts: Artifact[];
    handleArtifactClick: (artifactId: string) => void;
    profile: UserProfile;
    chatFontStyle: ChatFontStyle;
}

const getFontClass = (style: ChatFontStyle): string => {
    switch (style) {
        case 'Match System':
            return 'font-sans';
        case 'Dyslexic friendly':
            return 'font-dyslexic';
        default:
            return 'font-poppins';
    }
};

interface ImagePreviewProps {
    file: File;
}

const ImagePreview: React.FC<ImagePreviewProps> = ({ file }) => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <>
            <div
                className="cursor-pointer"
                onClick={() => setIsOpen(true)}
            >
                <img
                    src={URL.createObjectURL(file)}
                    alt={file.name}
                    className="w-20 h-20 object-cover rounded-md"
                />
            </div>

            <Dialog open={isOpen} onOpenChange={setIsOpen}>
                <DialogContent className="sm:max-w-[90vw] sm:max-h-[90vh] w-full h-full flex items-center justify-center">
                    <DialogClose className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground">
                        <X className="h-4 w-4" />
                        <span className="sr-only">Close</span>
                    </DialogClose>
                    <img
                        src={URL.createObjectURL(file)}
                        alt={file.name}
                        className="max-w-full max-h-full object-contain"
                    />
                </DialogContent>
            </Dialog>
        </>
    );
};


export const ChatArea: React.FC<ChatAreaProps> = ({
    messages,
    artifacts,
    handleArtifactClick,
    profile,
    chatFontStyle
}) => {
    const fontClass = getFontClass(chatFontStyle);

    const isImageFile = (file: File) => {
        return file.type.startsWith('image/');
    };

    return (
        <div className={`chat-area flex-1 mb-4 p-3 ${fontClass}`}>
            {messages.map((message, index) => {
                const nextMessage = messages[index + 1];
                const showArtifact = nextMessage && nextMessage.role === 'artifact';

                return (
                    <div key={index} className={`mb-4 ${message.role === "user" ? "text-left" : "text-left"}`}>
                        {message.role === "user" && (
                            <div className="flex flex-col items-end">
                                {message.files && message.files.length > 0 && (
                                    <div className="mt-2 flex flex-wrap gap-2 justify-end">
                                        {message.files.map((file, fileIndex) => {
                                            if (isImageFile(file)) {
                                                return (
                                                    <ImagePreview key={fileIndex} file={file} />
                                                );
                                            } else {
                                                const fileName = file.name;
                                                const dotIndex = fileName.lastIndexOf(".");
                                                const name = dotIndex !== -1 ? fileName.substring(0, dotIndex) : fileName;
                                                const extension = dotIndex !== -1 ? fileName.substring(dotIndex) : "";
                                                const truncatedName = name.length > 16 ? `${name.substring(0, 13)}...` : name;

                                                return (
                                                    <div key={fileIndex} className="flex items-center gap-2 p-2 border rounded-md bg-[hsl(var(--accent))]">
                                                        <div className="p-2 bg-gray-700 rounded">
                                                            <FileText className="w-5 h-5 text-white" />
                                                        </div>
                                                        <span className="text-sm text-[hsl(var(--accent-foreground))]">
                                                            {truncatedName}
                                                            <span>{extension}</span>
                                                        </span>
                                                    </div>
                                                );
                                            }
                                        })}
                                    </div>
                                )}
                                <span className="inline-block mt-2 p-2 rounded-lg bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]">
                                    {message.content}
                                </span>
                            </div>
                        )}

                        {message.role === "assistant_pending" && (
                            <div className="flex flex-col items-start">
                                <div className="flex items-start gap-3">
                                    <div className="p-2 rounded-full border border-[hsl(var(--primary))] bg-[hsl(var(--muted))]">
                                        <Brain className="w-5 h-5 text-[hsl(var(--primary))]" />
                                    </div>
                                    <span className="waiting-text inline-block p-2 rounded-lg">
                                        <span className="waving-text text-sm italic">
                                            {message.content}
                                        </span>
                                    </span>
                                </div>
                            </div>
                        )}

                        {message.role === "assistant" && (
                            <div className="flex flex-col items-start">
                                <div className="flex items-start gap-3">
                                    <div className="p-2 rounded-full border border-[hsl(var(--primary))] bg-[hsl(var(--muted))]">
                                        <Brain className="w-5 h-5 text-[hsl(var(--primary))]" />
                                    </div>
                                    <div className="flex flex-col p-2 rounded-lg bg-[hsl(var(--muted))] text-[hsl(var(--foreground))]">
                                        <span className="inline-block">
                                            {message.content}
                                        </span>
                                        {showArtifact && hasMinimumProfileLevel(profile, 2) && nextMessage.artifactId && (
                                            <>
                                                <ArtifactCard
                                                    artifact={artifacts.find(a => a.id === nextMessage.artifactId)!}
                                                    handleArtifactClick={handleArtifactClick}
                                                />
                                                {nextMessage.summary && (
                                                    <span className="inline-block">
                                                        {nextMessage.summary}
                                                    </span>
                                                )}
                                            </>
                                        )}
                                    </div>
                                </div>

                                {hasMinimumProfileLevel(profile, 1) && message.component && message.data && (
                                    <div className="mt-4 w-full">
                                        <DynamicComponent
                                            component={message.component as "Table" | "Chart" | "Card" | "Text"}
                                            data={message.data}
                                        />
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
};

const ArtifactCard: React.FC<{ artifact: Artifact; handleArtifactClick: (artifactId: string) => void }> = ({ artifact, handleArtifactClick }) => (
    <Card
        className="mt-2 mb-2 inline-block"
        onClick={() => handleArtifactClick(artifact.id)}
        style={{ boxShadow: 'none', maxWidth: 'fit-content' }}
    >
        <CardContent className="flex items-center gap-4 p-4 cursor-pointer border-[hsl(var(--border))]">
            <div className="p-2 bg-gray-700 rounded">
                {artifact.isLoading ? (
                    <SpokeSpinner />
                ) : (
                    <CodeXml className="w-6 h-6 text-[hsl(var(--primary-foreground))]" />
                )}
            </div>
            <div className="flex-grow min-w-0">
                <p className="text-sm font-medium text-[hsl(var(--foreground))]">{artifact.title}</p>
                <p className="text-xs text-[hsl(var(--muted-foreground))] ">
                    {artifact.isLoading ? 'Generating component...' : `Click to open component • ${artifact.version} version(s)`}
                </p>
            </div>
        </CardContent>
    </Card>
);
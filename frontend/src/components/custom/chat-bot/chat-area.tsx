// File: src/components/custom/chat-bot/chat-area.tsx

import React, { useState, useEffect } from 'react';
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
    files?: FileAttachment[];
    component?: "Table" | "Chart" | "Card" | "Text";
    data?: any;
    artifactId?: string;
    summary?: string;
    id?: string;
}

interface FileAttachment {
    name: string;
    type: string;
    size?: number;
    downloadUrl: string;
    storagePath?: string;
    fileDetails?: any;
}

interface ImagePreviewProps {
    file: FileAttachment;
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
    onShowChatArtifacts: React.Dispatch<React.SetStateAction<boolean>>;
    setArtifactsData: React.Dispatch<React.SetStateAction<any>>;

}

const getFontClass = (style: ChatFontStyle): string => {
    try {
        switch (style) {
            case 'Match System':
                return 'font-sans';
            case 'Dyslexic friendly':
                return 'font-dyslexic';
            default:
                return 'font-poppins';
        }
    } catch (error) {
        console.error('Error in getFontClass:', error);
        return 'font-sans';
    }
};

const ImagePreview: React.FC<ImagePreviewProps> = ({ file }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [imageError, setImageError] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    console.log("File object received:", file);
    console.log("Download URL:", file.downloadUrl);
    console.log("Storage path:", file.storagePath);

    // Function to get correct URL for MinIO
    const getImageUrl = (url: string) => {
        // Always use the permanent bucket
        if (url.includes('/chat-attachments/')) {
            return url.replace('/chat-attachments/', '/permanent/');
        }
        return url;
    };

    const handleImageLoad = () => {
        setIsLoading(false);
        setImageError(false);
    };

    const handleImageError = () => {
        console.error('Error loading image:', file.name);
        setImageError(true);
        setIsLoading(false);
    };

    const handleDownload = async (e: React.MouseEvent) => {
        e.stopPropagation();
        try {
            setIsLoading(true);
            const imageUrl = getImageUrl(file.downloadUrl);
            const response = await fetch(imageUrl);

            if (!response.ok) throw new Error('Download failed');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = file.name;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error('Download error:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const imageUrl = getImageUrl(file.downloadUrl);

    return (
        <>
            <div className="relative cursor-pointer group" onClick={() => setIsOpen(true)}>
                {isLoading && (
                    <div className="absolute inset-0 flex items-center justify-center bg-muted rounded-md">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                    </div>
                )}
                {!imageError ? (
                    <>
                        <img
                            src={imageUrl} 
                            alt={file.name}
                            className={`w-20 h-20 object-cover rounded-md transition-opacity duration-200 ${isLoading ? 'opacity-0' : 'opacity-100'
                                }`}
                            onError={handleImageError}
                            onLoad={handleImageLoad}
                        />
                        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all duration-200 flex items-center justify-center rounded-md">
                            <button
                                onClick={handleDownload}
                                className="opacity-0 group-hover:opacity-100 bg-white text-black px-2 py-1 rounded text-xs"
                                disabled={isLoading}
                            >
                                {isLoading ? 'Loading...' : 'Download'}
                            </button>
                        </div>
                    </>
                ) : (
                    <div className="w-20 h-20 bg-muted flex items-center justify-center rounded-md">
                        <span className="text-xs text-muted-foreground">Image Error</span>
                    </div>
                )}
            </div>

            <Dialog open={isOpen} onOpenChange={setIsOpen}>
                <DialogContent className="sm:max-w-[90vw] sm:max-h-[90vh] w-full h-full flex items-center justify-center">
                    <DialogClose className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100">
                        <X className="h-4 w-4" />
                        <span className="sr-only">Close</span>
                    </DialogClose>
                    {!imageError ? (
                        <div className="relative">
                            <img
                                src={file.downloadUrl}
                                alt={file.name}
                                className="max-w-full max-h-[80vh] object-contain"
                                onError={handleImageError}
                            />
                            <button
                                onClick={handleDownload}
                                className="absolute bottom-4 right-4 bg-white text-black px-4 py-2 rounded shadow-lg hover:bg-gray-100"
                            >
                                Download
                            </button>
                        </div>
                    ) : (
                        <div className="p-4 text-center">
                            <span className="text-muted-foreground">Failed to load image</span>
                        </div>
                    )}
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
    chatFontStyle,
    onShowChatArtifacts,
    setArtifactsData
}) => {
    const fontClass = getFontClass(chatFontStyle);

    const isImageFile = (file: any) => {
        try {
            return Boolean(file?.type && typeof file.type === 'string' && file.type.startsWith('image/'));
        } catch (error) {
            console.error('Error checking file type:', error);
            return false;
        }
    };

    const handleArtifactCardClick = (artifact: Artifact) => {
        if (artifact && artifact.component) {
            setArtifactsData({
                component: artifact.component,
                data: artifact.data,
                title: artifact.title
            });

            onShowChatArtifacts(true);

            handleArtifactClick(artifact.id);
        }
    };

    const ArtifactCard: React.FC<{
        artifact: Artifact;
        messageId: string;
    }> = ({ artifact, messageId }) => {
        if (!artifact) return null;

        return (
            <Card
                className="mt-2 mb-2 inline-block cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => handleArtifactCardClick(artifact)}
                style={{ boxShadow: 'none', maxWidth: 'fit-content' }}
            >
                <CardContent className="flex items-center gap-4 p-4 border-[hsl(var(--border))]">
                    <div className="p-2 bg-gray-700 rounded">
                        {artifact.isLoading ? (
                            <SpokeSpinner />
                        ) : (
                            <CodeXml className="w-6 h-6 text-[hsl(var(--primary-foreground))]" />
                        )}
                    </div>
                    <div className="flex-grow min-w-0">
                        <p className="text-sm font-medium text-[hsl(var(--foreground))]">
                            {artifact.title || 'Generated Artifact'}
                        </p>
                        <p className="text-xs text-[hsl(var(--muted-foreground))]">
                            {artifact.isLoading ? 'Generating component...' : 'Click to view component'}
                        </p>
                    </div>
                </CardContent>
            </Card>
        );
    };

    const renderMessage = (message: Message, index: number) => {
        try {
            const nextMessage = messages[index + 1];
            const showArtifact = nextMessage && nextMessage.role === 'artifact';
            const artifactData = showArtifact ? artifacts.find(a => a.id === nextMessage.artifactId) : null;

            return (
                <div key={index} className={`mb-4 ${message.role === "user" ? "text-left" : "text-left"}`}>
                    {message.role === "user" && (
                        <div className="flex flex-col items-end">
                            {message.files && message.files.length > 0 && (
                                <div className="mt-2 flex flex-wrap gap-2 justify-end">
                                    {message.files.map((file, fileIndex) => {
                                        try {
                                            if (isImageFile(file) && file.downloadUrl) {
                                                return (
                                                    <ImagePreview key={fileIndex} file={file} />
                                                );
                                            } else {
                                                return (
                                                    <div key={fileIndex} className="flex items-center gap-2 p-2 border rounded-md bg-[hsl(var(--accent))]">
                                                        <div className="p-2 bg-gray-700 rounded">
                                                            <FileText className="w-5 h-5 text-white" />
                                                        </div>
                                                        <div className="flex flex-col">
                                                            <span className="text-sm text-[hsl(var(--accent-foreground))]">
                                                                {file.name}
                                                            </span>
                                                            <a
                                                                href={file.downloadUrl}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                className="text-xs text-blue-500 hover:text-blue-600"
                                                                onClick={(e) => {
                                                                    e.stopPropagation();
                                                                    e.preventDefault();
                                                                    window.open(file.downloadUrl, '_blank');
                                                                }}
                                                            >
                                                                Download
                                                            </a>
                                                        </div>
                                                    </div>
                                                );
                                            }
                                        } catch (error) {
                                            console.error('Error rendering file:', error);
                                            return (
                                                <div key={fileIndex} className="p-2 border rounded-md bg-red-50">
                                                    <span className="text-sm text-red-500">Error displaying file</span>
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
                                    {message.files && message.files.length > 0 && (
                                        <div className="mt-2 flex flex-wrap gap-2">
                                            {message.files.map((file, fileIndex) => {
                                                if (isImageFile(file)) {
                                                    return (
                                                        <ImagePreview key={fileIndex} file={file} />
                                                    );
                                                } else {
                                                    return (
                                                        <div key={fileIndex} className="flex items-center gap-2 p-2 border rounded-md bg-[hsl(var(--accent))]">
                                                            <div className="p-2 bg-gray-700 rounded">
                                                                <FileText className="w-5 h-5 text-white" />
                                                            </div>
                                                            <div className="flex flex-col">
                                                                <span className="text-sm text-[hsl(var(--accent-foreground))]">
                                                                    {file.name}
                                                                </span>
                                                                <a
                                                                    href={file.downloadUrl}
                                                                    target="_blank"
                                                                    rel="noopener noreferrer"
                                                                    className="text-xs text-blue-500 hover:text-blue-600"
                                                                >
                                                                    Download
                                                                </a>
                                                            </div>
                                                        </div>
                                                    );
                                                }
                                            })}
                                        </div>
                                    )}
                                    <span className="inline-block">
                                        {message.content}
                                    </span>
                                </div>
                            </div>

                            {hasMinimumProfileLevel(profile, 1) && message.component && message.data && (
                                <div className="mt-4 w-full">
                                    <ErrorBoundary>
                                        <DynamicComponent
                                            component={message.component as "Table" | "Chart" | "Card" | "Text"}
                                            data={message.data}
                                        />
                                    </ErrorBoundary>
                                </div>
                            )}
                        </div>
                    )}

                </div>
            );
        } catch (error) {
            console.error('Error rendering message:', error);
            return (
                <div key={index} className="p-4 mb-4 border rounded-md bg-red-50">
                    <span className="text-sm text-red-500">Error displaying message</span>
                </div>
            );
        }
    };

    return (
        <div className={`chat-area flex-1 mb-4 p-3 ${fontClass}`}>
            {messages.map((message, index) => {
                try {
                    return renderMessage(message, index);
                } catch (error) {
                    console.error('Error in message rendering:', error);
                    return (
                        <div key={index} className="p-4 mb-4 border rounded-md bg-red-50">
                            <span className="text-sm text-red-500">Error displaying message</span>
                        </div>
                    );
                }
            })}
        </div>
    );
};

// Error Boundary Component
class ErrorBoundary extends React.Component<{ children: React.ReactNode }, { hasError: boolean }> {
    constructor(props: { children: React.ReactNode }) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError() {
        return { hasError: true };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        console.error('Error in component:', error);
        console.error('Error info:', errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="p-4 border rounded-md bg-red-50">
                    <span className="text-sm text-red-500">Error rendering component</span>
                </div>
            );
        }

        return this.props.children;
    }
}

// const ArtifactCard: React.FC<{ artifact: Artifact; handleArtifactClick: (artifactId: string) => void }> = ({ artifact, handleArtifactClick }) => {
//     try {
//         return (
//             <Card
//                 className="mt-2 mb-2 inline-block"
//                 onClick={() => handleArtifactClick(artifact.id)}
//                 style={{ boxShadow: 'none', maxWidth: 'fit-content' }}
//             >
//                 <CardContent className="flex items-center gap-4 p-4 cursor-pointer border-[hsl(var(--border))]">
//                     <div className="p-2 bg-gray-700 rounded">
//                         {artifact.isLoading ? (
//                             <SpokeSpinner />
//                         ) : (
//                             <CodeXml className="w-6 h-6 text-[hsl(var(--primary-foreground))]" />
//                         )}
//                     </div>
//                     <div className="flex-grow min-w-0">
//                         <p className="text-sm font-medium text-[hsl(var(--foreground))]">{artifact.title}</p>
//                         <p className="text-xs text-[hsl(var(--muted-foreground))] ">
//                             {artifact.isLoading ? 'Generating component...' : `Click to open component • ${artifact.version} version(s)`}
//                         </p>
//                     </div>
//                 </CardContent>
//             </Card>
//         );
//     } catch (error) {
//         console.error('Error rendering artifact card:', error);
//         return (
//             <div className="p-4 border rounded-md bg-red-50">
//                 <span className="text-sm text-red-500">Error displaying artifact</span>
//             </div>
//         );
//     }
// };
// File: src/types/chat.ts

export interface UploadedFile extends File {
    documentId: number;
}

export interface Message {
    id: string;
    content: string;
    role: string;
    timestamp?: string;
    attachments?: any[];
    metadata?: any;
}

export interface Artifact {
    id: string;
    title: string;
    component: string;
    data: any;
    version: number;
    isLoading?: boolean;
}

// Add the ChatCollection interface
export interface Conversation {
    id: number;
    title: string;
    last_message_at: string;
    message_count: number;
}

export interface ChatCollection {
    id: number;
    collection_name: string;
    created_at: string;
    conversation_count: number;
    conversations: Conversation[];
}

export interface FileHandlingProps {
    attachedFiles: UploadedFile[];
    setAttachedFiles: React.Dispatch<React.SetStateAction<UploadedFile[]>>;
    uploadingFiles: Record<number, boolean>;
    setUploadingFiles: React.Dispatch<React.SetStateAction<Record<number, boolean>>>;
    handleFileInput: (e: React.ChangeEvent<HTMLInputElement>) => Promise<void>;
    removeFile: (index: number) => Promise<void>;
}

export interface MessageHandlingProps {
    inputMessage: string;
    setInputMessage: React.Dispatch<React.SetStateAction<string>>;
    handleSendMessage: (e: React.FormEvent | React.KeyboardEvent) => Promise<void>;
    handleInputChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
    handleKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void;
    isSendDisabled: boolean;
}
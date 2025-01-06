// File: src/types/chat.ts

export interface Message {
    id: string;
    role: 'user' | 'assistant' | 'assistant_pending';
    content: string;
    files?: UploadedFile[];
    artifactId?: string;
    component?: string;
    data?: any;
    artifactTitle?: string; 
    isNew?: boolean; 
    messageId?: string;
}

export interface UploadedFile extends File {
    documentId?: number;
    downloadUrl: string;
    storagePath: string;
    fileDetails?: any;
}

export interface FileAttachment {
    name: string;
    type: string;
    size: number;
    downloadUrl: string;
    storagePath: string;
    fileDetails?: any;
}

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
    platform: string;
    is_platform_changed: boolean;
    platform_changed: string | null;
}
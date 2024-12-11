// src/utils/fileHandlers.ts

import { ImageFileDetails, VideoFileDetails, DocumentFileDetails, BaseFileDetails } from "@/types/file";

export const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const getImageDetails = async (file: File): Promise<ImageFileDetails> => {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => {
            URL.revokeObjectURL(img.src); 
            resolve({
                size: file.size,
                type: file.type,
                name: file.name,
                lastModified: file.lastModified,
                sizeFormatted: formatFileSize(file.size),
                width: img.width,
                height: img.height,
                aspectRatio: img.width / img.height
            });
        };
        img.onerror = () => reject(new Error('Failed to load image'));
        img.src = URL.createObjectURL(file);
    });
};

export const getVideoDetails = async (file: File): Promise<VideoFileDetails> => {
    return new Promise((resolve, reject) => {
        const video = document.createElement('video');
        video.preload = 'metadata';
        
        video.onloadedmetadata = () => {
            URL.revokeObjectURL(video.src);
            resolve({
                size: file.size,
                type: file.type,
                name: file.name,
                lastModified: file.lastModified,
                sizeFormatted: formatFileSize(file.size),
                duration: video.duration,
                width: video.videoWidth,
                height: video.videoHeight,
                aspectRatio: video.videoWidth / video.videoHeight
            });
        };
        
        video.onerror = () => reject(new Error('Failed to load video'));
        video.src = URL.createObjectURL(file);
    });
};

export const getDocumentDetails = async (file: File): Promise<DocumentFileDetails> => {
    const details: DocumentFileDetails = {
        size: file.size,
        type: file.type,
        name: file.name,
        lastModified: file.lastModified,
        sizeFormatted: formatFileSize(file.size)
    };

    if (file.type === 'application/pdf') {
        details.type = 'PDF Document';
    } else if (file.type === 'application/msword' || file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
        details.type = 'Word Document';
    } else if (file.type === 'application/vnd.ms-powerpoint' || file.type === 'application/vnd.openxmlformats-officedocument.presentationml.presentation') {
        details.type = 'PowerPoint Presentation';
    } else if (file.type === 'text/plain') {
        details.type = 'Text Document';
    }

    return details;
};

export const processFile = async (file: File): Promise<BaseFileDetails | ImageFileDetails | VideoFileDetails | DocumentFileDetails> => {
    if (file.type === 'text/plain') {
        return await getDocumentDetails(file);
    }
    
    const fileType = file.type.split('/')[0];
    
    try {
        switch (fileType) {
            case 'image':
                return await getImageDetails(file);
                
            case 'video':
                return await getVideoDetails(file);
                
            case 'application':
                return await getDocumentDetails(file);
                
            default:
                return {
                    size: file.size,
                    type: file.type,
                    name: file.name,
                    lastModified: file.lastModified,
                    sizeFormatted: formatFileSize(file.size)
                };
        }
    } catch (error) {
        console.error(`Error processing ${fileType} file:`, error);
        throw error;
    }
};

export const validateFile = (file: File, maxSize: number = 5 * 1024 * 1024): string | null => {
    if (file.size > maxSize) {
        return `File size exceeds ${formatFileSize(maxSize)} limit`;
    }

    const allowedTypes = [
        'image/jpeg',
        'image/png',
        'image/gif',
        'video/mp4',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'text/plain'  
    ];

    if (!allowedTypes.includes(file.type)) {
        return 'File type not supported';
    }

    return null; 
};
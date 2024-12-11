// src/types/file.ts

export interface BaseFileDetails {
    size: number;
    type: string;
    name: string;
    lastModified: number;
    sizeFormatted: string;
}

export interface ImageFileDetails extends BaseFileDetails {
    width: number;
    height: number;
    aspectRatio: number;
}

export interface VideoFileDetails extends BaseFileDetails {
    duration: number;
    width: number;
    height: number;
    aspectRatio: number;
}

export interface DocumentFileDetails extends BaseFileDetails {
    pageCount?: number;
}

export interface UploadedFile extends File {
    documentId?: number;  
    downloadUrl: string;
    storagePath: string;
    fileDetails?: any;
}
// File: src/components/custom/chat-bot/chat-form.tsx

import React, { useEffect, useRef, useState } from 'react';
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Paperclip, Mic, CornerDownLeft, X, Camera, FileIcon, ImageIcon, AudioLines } from "lucide-react";
import { Tooltip, TooltipTrigger, TooltipContent } from "@/components/ui/tooltip";
import { SpokeSpinner, UpdatedSpokeSpinner } from "../../ui/spinner";
import VoiceRecordingInterface from './chat-form-interface/voice-record-interface';
import { motion, AnimatePresence } from 'framer-motion';
import { useToast } from '@/hooks/use-toast';
import { ToastAction } from '@/components/ui/toast';
import { ImagePreview, FilePreview } from './Preview';
import Speech from './chat-form-interface/speech-to-speech-interface';
import { validateFile, processFile } from '@/utils/fileHandlers';
import { ImageFileDetails, VideoFileDetails, DocumentFileDetails } from '@/types/file';
import { pasteValidator, PasteValidator } from '@/utils/pasteValidator';
import { supabase } from '@/lib/supabase';

interface UploadedFile extends File {
    downloadUrl: string;
    storagePath: string;
    fileDetails?: any;
}

interface ChatFormProps {
    inputMessage: string;
    setInputMessage: React.Dispatch<React.SetStateAction<string>>;
    handleSendMessage: (e: React.FormEvent, files: UploadedFile[]) => Promise<void>;
    handleInputChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
    isSendDisabled: boolean;
}

const MAX_ATTACHMENTS = 5;
const MAX_FILE_SIZE = 5 * 1024 * 1024;

export const ChatForm: React.FC<ChatFormProps> = ({
    inputMessage,
    setInputMessage,
    handleSendMessage,
    handleInputChange,
    isSendDisabled,
}) => {
    const { toast } = useToast();
    const fileInputRef = useRef<HTMLInputElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement | null>(null);
    const [isRecording, setIsRecording] = useState(false);
    const [isScreenshotting, setIsScreenshotting] = useState(false);
    const [attachedFiles, setAttachedFiles] = useState<UploadedFile[]>([]);
    const [uploadingFiles, setUploadingFiles] = useState<Record<number, boolean>>({});
    const [isUploading, setIsUploading] = useState(false);

    const handlePaste = async (e: React.ClipboardEvent<HTMLTextAreaElement>) => {
        const validationResult = await pasteValidator.validatePaste(
            e.clipboardData,
            attachedFiles.length,
            uploadToSupabase
        );
    
        if (!validationResult.isValid && validationResult.shouldCreateFile) {
            e.preventDefault();
            setIsUploading(true); 
            
            if (validationResult.processedFile) {
                const uploadedFile = await uploadToSupabase(validationResult.processedFile);
                if (uploadedFile) {
                    setAttachedFiles(prev => [...prev, uploadedFile]);
                }
            }
            setIsUploading(false); 
        }
    };

    const uploadToSupabase = async (file: File): Promise<UploadedFile | null> => {
        const validationError = validateFile(file);
        if (validationError) {
            console.error('Validation Failed:', validationError);
            console.groupEnd();
            toast({
                title: "Invalid File",
                description: validationError,
                variant: "destructive",
                className: "font-poppins",
                action: <ToastAction altText="Okay">Okay</ToastAction>,
            });
            return null;
        }
    
        try {
            const fileDetails = await processFile(file);
            console.log('Processed File Detailss :', fileDetails);
    
            const timestamp = Date.now();
            const fileName = `${timestamp}-${file.name}`;
            const storagePath = `temp/${fileName}`; 
    
            const { data: uploadData, error: uploadError } = await supabase.storage
                .from('chat-attachments') 
                .upload(storagePath, file, {
                    cacheControl: '3600',
                    contentType: file.type,
                    upsert: false
                });
    
            if (uploadError) throw uploadError;
    
            const { data: { publicUrl } } = supabase.storage
                .from('chat-attachments')
                .getPublicUrl(storagePath);
    
            const result = Object.assign(file, {
                downloadUrl: publicUrl,
                storagePath,
                fileDetails
            }) as UploadedFile;
    
            console.log('Final Results:', result);
            console.groupEnd();
            return result;
    
        } catch (error) {
            console.error("Upload Error:", error);
            console.groupEnd();
            toast({
                title: "Upload Failed",
                description: `Failed to upload ${file.name}. Please try again.`,
                variant: "destructive",
                className: "font-poppins",
                action: <ToastAction altText="Okay">Okay</ToastAction>,
            });
            return null;
        }
    };

    const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || []);

        if (attachedFiles.length + files.length > MAX_ATTACHMENTS) {
            toast({
                title: "Too Many Files",
                description: `You can only attach up to ${MAX_ATTACHMENTS} files in total.`,
                variant: "destructive",
                className: "font-poppins",
                action: <ToastAction altText="Okay">Okay</ToastAction>,
            });
            return;
        }

        setIsUploading(true);

        try {
            const uploadedFiles = await Promise.all(
                files.map(async (file) => {
                    const result = await uploadToSupabase(file);
                    return result;
                })
            );

            const validFiles = uploadedFiles.filter((file): file is UploadedFile => file !== null);
            setAttachedFiles((prevFiles) => [...prevFiles, ...validFiles]);
        } catch (error) {
            console.error('Upload error:', error);
            toast({
                title: "Upload Failed",
                description: "Failed to upload files. Please try again.",
                variant: "destructive",
                className: "font-poppins",
                action: <ToastAction altText="Okay">Okay</ToastAction>,
            });
        } finally {
            setIsUploading(false);
        }
    };

    const removeFile = async (index: number) => {
        const fileToRemove = attachedFiles[index];
    
        if (fileToRemove && fileToRemove.storagePath) {
            try {
                const { error } = await supabase.storage
                    .from('chat-attachments')
                    .remove([fileToRemove.storagePath]);
    
                if (error) throw error;
    
                setAttachedFiles((prevFiles) => prevFiles.filter((_, i) => i !== index));
    
            } catch (error) {
                console.error("Error removing file:", error);
                toast({
                    title: "Error",
                    description: "Failed to remove file. Please try again.",
                    variant: "destructive",
                    className: "font-poppins",
                    action: <ToastAction altText="Okay">Okay</ToastAction>,
                });
            }
        }
    };

    const handleFileDrop = async (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        const files = Array.from(e.dataTransfer.files);

        if (attachedFiles.length + files.length > MAX_ATTACHMENTS) {
            toast({
                title: "Too Many Files",
                description: `You can only attach up to ${MAX_ATTACHMENTS} files in total.`,
                variant: "destructive",
                className: "font-poppins",
                action: <ToastAction altText="Okay">Okay</ToastAction>,
            });
            return;
        }

        setIsUploading(true);

        try {
            const uploadedFiles = await Promise.all(
                files.map(async (file) => {
                    const result = await uploadToSupabase(file);
                    return result;
                })
            );

            const validFiles = uploadedFiles.filter((file): file is UploadedFile => file !== null);
            setAttachedFiles((prevFiles) => [...prevFiles, ...validFiles]);
        } catch (error) {
            console.error('Upload error:', error);
            toast({
                title: "Upload Failed",
                description: "Failed to upload files. Please try again.",
                variant: "destructive",
                className: "font-poppins",
                action: <ToastAction altText="Okay">Okay</ToastAction>,
            });
        } finally {
            setIsUploading(false);
        }
    };

    const handleSubmitWithFiles = (e: React.FormEvent) => {
        e.preventDefault();
        if (inputMessage.trim()) {
            console.log('Submitting with files:', attachedFiles);
            handleSendMessage(e, attachedFiles);
            setAttachedFiles([]);
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmitWithFiles(e as unknown as React.FormEvent);
        }
    };


    const handleMicClick = () => {
        setIsRecording(true);
    };

    const handleRecordingCancel = () => {
        setIsRecording(false);
    };

    const handleRecordingSave = (transcribedText: string) => {
        setInputMessage((prevMessage) => {
            const newMessage = prevMessage.trim() ? `${prevMessage.trim()} ${transcribedText}` : transcribedText;

            setTimeout(() => {
                if (textareaRef.current) {
                    textareaRef.current.focus();
                    textareaRef.current.selectionStart = textareaRef.current.value.length;
                    textareaRef.current.selectionEnd = textareaRef.current.value.length;
                }
            }, 500);

            return newMessage;
        });
        setIsRecording(false);
    };

    const handleScreenshot = async () => {
        if (attachedFiles.length >= MAX_ATTACHMENTS) {
            toast({
                title: "Maximum Attachments Reached",
                description: `You can only attach up to ${MAX_ATTACHMENTS} files.`,
                variant: "destructive",
                className: "font-poppins",
                action: <ToastAction altText="Okay">Okay</ToastAction>,
            });
            return;
        }

        setIsScreenshotting(true);
        try {
            const html2canvas = (await import('html2canvas')).default;
            const canvas = await html2canvas(document.body);
            canvas.toBlob(async (blob) => {
                if (blob) {
                    if (blob.size > MAX_FILE_SIZE) {
                        toast({
                            title: "Screenshot Too Large",
                            description: "The screenshot exceeds the 5 MB limit. Please try capturing a smaller area.",
                            variant: "destructive",
                            className: "font-poppins",
                            action: <ToastAction altText="Okay">Okay</ToastAction>,
                        });
                        return;
                    }

                    const file = new File([blob], `screenshot-${Date.now()}.png`, { type: 'image/png' });
                    const uploadedFile = await uploadToSupabase(file);
                    if (uploadedFile) {
                        setAttachedFiles(prevFiles => [...prevFiles, uploadedFile]);
                        setIsScreenshotting(false);

                    }
                }
            }, 'image/png');
        } catch (error) {
            console.error('Error taking screenshot:', error);
            toast({
                title: "Screenshot Failed",
                description: "An error occurred while capturing the screenshot. Please try again.",
                variant: "destructive",
                className: "font-poppins",
                action: <ToastAction altText="Okay">Okay</ToastAction>,
            });
        } finally {
            // setIsScreenshotting(false);
        }
    };

    const handleFileButtonClick = () => {
        if (attachedFiles.length >= MAX_ATTACHMENTS) {
            toast({
                title: "Maximum Attachments Reached",
                description: `You can only attach up to ${MAX_ATTACHMENTS} files.`,
                variant: "destructive",
                className: "font-poppins",
                action: <ToastAction altText="Okay">Okay</ToastAction>,
            });
        } else {
            fileInputRef.current?.click();
        }
    };

    const formatFileSize = (bytes: number): string => {
        if (isNaN(bytes) || bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const isImageFile = (file: File) => {
        return file.type.startsWith('image/');
    };

    const [isSpeechDialogShowing, setIsSpeechDialogShowing] = useState(false);

    const handleSpeechDialogClick = () => {
        setIsSpeechDialogShowing(true);
    };

    const formClasses = `vibrant-chat-form sticky bottom-0 left-0 rounded-lg z-20 pt-1 ${isRecording ? '' : 'border bg-[hsl(var(--background))] focus-within:ring-1 focus-within:ring-[hsl(var(--ring))]'
        }`;

    return (
        <div className={formClasses}
            onDrop={handleFileDrop}
            onDragOver={(e) => e.preventDefault()}
        >
            <AnimatePresence>
                {attachedFiles.length > 0 && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.3 }}
                        className="attachments-container mb-2 flex flex-row flex-wrap gap-2 overflow-x-auto max-w-full p-2"
                    >
                        {attachedFiles.map((file, index) => (
                            isImageFile(file) ? (
                                <ImagePreview
                                    key={index}
                                    file={file}
                                    onRemove={() => removeFile(index)}
                                />
                            ) : (
                                <FilePreview
                                    key={index}
                                    file={file}
                                    onRemove={() => removeFile(index)}
                                    isUploading={!!uploadingFiles[index]}
                                />
                            )
                        ))}
                    </motion.div>
                )}
            </AnimatePresence>

            <AnimatePresence mode="wait">
                {isRecording ? (
                    <motion.div
                        key="voice-recording"
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -5 }}
                        transition={{
                            type: "tween",
                            ease: "easeInOut",
                            duration: 0.3
                        }}
                    >
                        <VoiceRecordingInterface onCancel={handleRecordingCancel} onSave={handleRecordingSave} />
                    </motion.div>
                ) : (
                    <>
                        <form onSubmit={handleSubmitWithFiles}>
                            <Textarea
                                id="message"
                                placeholder="Type your message here..."
                                className="resize-none border-0 p-3 shadow-none focus-visible:ring-0 text-[hsl(var(--foreground))]"
                                value={inputMessage}
                                onChange={handleInputChange}
                                onKeyDown={handleKeyDown}
                                onPaste={handlePaste}
                                autoFocus
                                ref={textareaRef}
                                disabled={isUploading}
                            />
                        </form>

                        <div className="flex items-center p-3 pt-0">
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        onClick={handleFileButtonClick}
                                        disabled={isUploading || attachedFiles.length >= MAX_ATTACHMENTS}
                                    >
                                        {isUploading ? (
                                            <UpdatedSpokeSpinner className='text-[hsl(var(--foreground))]' />
                                        ) : (
                                            <Paperclip className="size-4 text-[hsl(var(--foreground))]" />
                                        )}
                                        <span className="sr-only">Attach file</span>
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent side="top">
                                    {isUploading
                                        ? "Uploading..."
                                        : attachedFiles.length >= MAX_ATTACHMENTS
                                            ? "Maximum attachments reached"
                                            : "Attach File"
                                    }
                                </TooltipContent>
                            </Tooltip>

                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Button variant="ghost"
                                        size="icon"
                                        onClick={handleMicClick}
                                        disabled={isUploading}
                                    >
                                        <Mic className="size-4 text-[hsl(var(--foreground))]" />
                                        <span className="sr-only">Use Microphone</span>
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent side="top">Use Microphone</TooltipContent>
                            </Tooltip>

                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Button variant="ghost"
                                        size="icon"
                                        onClick={handleScreenshot}
                                        disabled={isScreenshotting || isUploading}
                                    >
                                        {isScreenshotting ? (
                                            <SpokeSpinner />
                                        ) : (
                                            <Camera className="size-4 text-[hsl(var(--foreground))]" />
                                        )}
                                        <span className="sr-only">Take Screenshot</span>
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent side="top">Take Screenshot</TooltipContent>
                            </Tooltip>

                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Button variant="ghost"
                                        size="icon"
                                        onClick={handleSpeechDialogClick}
                                        disabled={isUploading}
                                    >
                                        <AudioLines className="size-4 text-[hsl(var(--foreground))]" />
                                        <span className="sr-only">Speech</span>
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent side="top">Speech</TooltipContent>
                            </Tooltip>

                            <Button
                                type="submit"
                                size="sm"
                                className="ml-auto gap-1.5 bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]"
                                disabled={isSendDisabled || isUploading}
                            >
                                Send Message
                                <CornerDownLeft className="size-3.5" />
                            </Button>
                        </div>
                    </>
                )}
            </AnimatePresence>

            <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                multiple
                onChange={handleFileInput}
                accept="image/*,application/pdf,.doc,.docx,.txt"
            />
            <Speech isOpen={isSpeechDialogShowing} onClose={() => setIsSpeechDialogShowing(false)} />

        </div>
    );
};
'use client'

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, Image, File, FileText as FileDoc, FileSpreadsheet, PaperclipIcon, Download } from 'lucide-react';
import BreadcrumbComponent from '@/components/custom/bread-crumb';
import NavigationComponent from '@/components/custom/pg_navigation';
import HeaderComponent from '@/components/custom/pg_header';
import { Button } from '@/components/ui/button';
import { SpokeSpinner } from '@/components/ui/spinner';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';

const identifyFileType = (fileName: string): FileType => {
    const extension = fileName.split('.').pop()?.toLowerCase();

    switch (extension) {
        case 'jpg':
        case 'jpeg':
        case 'png':
        case 'gif':
            return 'image';
        case 'pdf':
            return 'pdf';
        case 'doc':
        case 'docx':
            return 'doc';
        case 'xls':
        case 'xlsx':
            return 'xls';
        case 'mp4':
        case 'mkv':
        case 'avi':
            return 'video';
        default:
            return 'default';
    }
};

interface Chat {
    sender: string;
    message: string;
    file: string | null;
    fileType: FileType | undefined;
    fileName: string | undefined;
}

type FileType = 'image' | 'pdf' | 'doc' | 'xls' | 'video' | 'default';

const fileTypeMap: Record<FileType, { icon: JSX.Element | null; iconBgColor: string; label: string; borderColor: string; bgColorLighter: string }> = {
    image: {
        icon: <Image className="h-4 w-4 text-white" />,
        iconBgColor: 'bg-pink-500',
        label: 'Image',
        borderColor: 'border-pink-500',
        bgColorLighter: 'bg-pink-100',
    },
    pdf: {
        icon: <FileText className="h-4 w-4 text-white" />,
        iconBgColor: 'bg-red-500',
        label: 'PDF Document',
        borderColor: 'border-red-500',
        bgColorLighter: 'bg-red-100',
    },
    doc: {
        icon: <FileDoc className="h-4 w-4 text-white" />,
        iconBgColor: 'bg-blue-500',
        label: 'Word Document',
        borderColor: 'border-blue-500',
        bgColorLighter: 'bg-blue-100',
    },
    xls: {
        icon: <FileSpreadsheet className="h-4 w-4 text-white" />,
        iconBgColor: 'bg-green-500',
        label: 'Excel File',
        borderColor: 'border-green-500',
        bgColorLighter: 'bg-green-100',
    },
    video: {
        icon: <File className="h-4 w-4 text-white" />,
        iconBgColor: 'bg-purple-500',
        label: 'Video File',
        borderColor: 'border-purple-500',
        bgColorLighter: 'bg-purple-100',
    },
    default: {
        icon: <File className="h-4 w-4 text-white" />,
        iconBgColor: 'bg-gray-500',
        label: 'File',
        borderColor: 'border-gray-500',
        bgColorLighter: 'bg-gray-100',
    },
};

interface Attachment {
    fileType: FileType;
    fileName: string;
    fileUrl: string;
}

const fetchAttachments = async (chatId: string) => {
    const response = await fetch(`http://localhost:8000/get_attachments/${chatId}`);
    if (!response.ok) {
        throw new Error('Failed to fetch attachments');
    }

    const data = await response.json();
    return data.map((item: any) => ({
        fileType: identifyFileType(item.file_name),
        fileName: item.file_name,
        fileUrl: item.file_path,
    }));
};


const fetchChatHistory = async (chatId: string) => {
    const response = await fetch(`http://localhost:8000/get_chat_history/${chatId}`);
    if (!response.ok) {
        throw new Error('Failed to fetch chat history');
    }

    const data = await response.json();
    return data.map((item: any) => ({
        sender: item.role === 'user' ? 'user' : 'assistant',
        message: item.content || 'No content',
        file: item.file_name && item.file_path ? `${item.file_path}` : null,
        fileType: item.file_name ? identifyFileType(item.file_name) : undefined,
        fileName: item.file_name,
    }));
};

export default function ChatHistory() {
    const searchParams = useSearchParams();
    const chatId = searchParams.get('chatId');
    const [currentChat, setCurrentChat] = useState<Chat[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [attachments, setAttachments] = useState<Attachment[]>([]);  
    const [isAttachmentLoading, setIsAttachmentLoading] = useState(false);

    useEffect(() => {
        if (chatId) {
            setLoading(true);
            fetchChatHistory(chatId)
                .then((data) => {
                    setCurrentChat(data);
                    setLoading(false);
                })
                .catch((err) => {
                    setError('Failed to load chat history.');
                    setLoading(false);
                });
        } else {
            setCurrentChat([]);
        }
    }, [chatId]);

    const handleDownloadAll = () => {
        attachments.forEach((attachment) => {
            const link = document.createElement('a');
            link.href = attachment.fileUrl || '#';
            link.setAttribute('download', attachment.fileName);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
    };

    const handleOpenAttachments = async () => {
        if (chatId) {
            setIsAttachmentLoading(true);
            try {
                const data = await fetchAttachments(chatId);
                setAttachments(data);
            } catch (error) {
                setError('Failed to load attachments.');
            } finally {
                setIsAttachmentLoading(false);
            }
        }
    };

    const renderDialogAttachment = (fileType: FileType | undefined, fileName: string, fileUrl: string | null) => {
        const type = fileType ? fileTypeMap[fileType] : fileTypeMap['default'];
        const { icon, iconBgColor, label } = type;

        const handleDownload = async (filePath: string, fileName: string) => {
            try {
                const response = await fetch(`http://localhost:8000/download_file/?file_path=${encodeURIComponent(filePath)}`, {
                    method: 'GET',
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const downloadUrl = URL.createObjectURL(blob);

                    const link = document.createElement('a');
                    link.href = downloadUrl;
                    link.setAttribute('download', fileName);
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);

                    URL.revokeObjectURL(downloadUrl);
                } else {
                    console.error('Failed to download the file:', response.statusText);
                }
            } catch (error) {
                console.error('Error occurred during file download:', error);
            }
        };

        return (
            <Card className="w-full relative group">
                <CardContent className="flex items-center p-2">
                    <div className={`flex items-center justify-center w-8 h-8 ${iconBgColor} rounded-full`}>
                        {icon}
                    </div>
                    <div className="ml-2 flex-grow">
                        <span className="text-black font-medium text-sm truncate">{fileName}</span>
                        <span className="block text-gray-500 text-sm">{label}</span>
                    </div>
                    <Button
                        variant="ghost"
                        size="icon"
                        className="absolute right-4 opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={() => fileUrl && handleDownload(fileUrl, fileName)}  
                    >
                        <Download className="w-5 h-5" />
                    </Button>
                </CardContent>
            </Card>
        );
    };

    const renderChatAttachment = (fileType: FileType | undefined, fileUrl: string | null, fileName: string | undefined, sender: string) => {
        if (!fileUrl || !fileName) return null;

        const alignmentClass = sender === 'user' ? 'justify-end' : 'justify-start';
        const type = (fileType && fileTypeMap[fileType]) ? fileType : 'default';
        const { icon, iconBgColor, label, borderColor, bgColorLighter } = fileTypeMap[type];

        const getTruncatedFileName = (name: string) => {
            const ext = name.split('.').pop() || '';
            const nameWithoutExt = name.substring(0, name.length - ext.length - 1);

            return nameWithoutExt.length > 10
                ? `${nameWithoutExt.substring(0, 10)}...${ext}`
                : name;
        };

        const handleDownload = async (filePath: string, fileName: string) => {
            try {
                const response = await fetch(`http://localhost:8000/download_file/?file_path=${encodeURIComponent(filePath)}`, {
                    method: 'GET',
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const downloadUrl = URL.createObjectURL(blob);

                    const link = document.createElement('a');
                    link.href = downloadUrl;
                    link.setAttribute('download', fileName);
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);

                    URL.revokeObjectURL(downloadUrl);
                } else {
                    console.error('Failed to download the file:', response.statusText);
                }
            } catch (error) {
                console.error('Error occurred during file download:', error);
            }
        };

        return (
            <div className={`relative flex items-center gap-2 mb-2 ${alignmentClass}`}>
                <div
                    className={`flex items-center p-2 rounded-lg text-xs border-2 ${borderColor} ${bgColorLighter} w-full`}
                    style={{
                        maxWidth: '250px',
                    }}
                >
                    <div className="flex items-center relative w-full">
                        <div className={`flex items-center justify-center w-8 h-8 ${iconBgColor} rounded-full mr-3`}>
                            {icon}
                        </div>
                        <div className="flex flex-col truncate flex-grow">
                            <span className="text-black font-medium truncate">{getTruncatedFileName(fileName)}</span>
                            <span className="text-gray-500 text-sm">{label}</span>
                        </div>

                        <button
                            onClick={() => handleDownload(fileUrl, fileName)}  // Wrap handleDownload with necessary arguments
                            className="absolute right-0 p-1 rounded-full bg-gray-200 hover:bg-gray-300 transition-all duration-200 opacity-0 group-hover:opacity-100"
                            style={{ top: '50%', transform: 'translateY(-50%)' }}
                        >
                            <Download className="h-4 w-4 text-gray-700" />
                        </button>
                    </div>
                </div>

                <style jsx>{`
                    .relative:hover button {
                        opacity: 1; /* Show download button on hover */
                    }
                    .relative button {
                        opacity: 0; /* Hide download button initially */
                        transition: opacity 0.2s;
                    }
                `}</style>
            </div>
        );
    };

    return (
        <div className="grid h-screen w-full pl-[56px] font-poppins">
            <NavigationComponent defaultActive="data" />
            <div className="flex flex-col">
                <HeaderComponent />

                <BreadcrumbComponent
                    items={[
                        { label: 'Chat History', href: '/chat-history' },
                    ]}
                    separator=">"
                    currentPage="View Chats"
                />

                <div className="flex flex-col items-center justify-center w-full h-full p-6">
                    <Card className="w-full max-w-full">
                        <CardHeader className="flex flex-row items-center justify-between border-b mb-4" style={{ borderColor: 'hsl(var(--border))' }}>
                            <div>
                                <CardTitle>Chat History</CardTitle>
                                <CardDescription>
                                    {chatId ? `Viewing chat history of Chat ID: ${chatId}` : 'Select a chat from the history'}
                                </CardDescription>
                            </div>

                            {/* Dialog for Attachments */}
                            <Dialog onOpenChange={handleOpenAttachments}>
                                <DialogTrigger asChild>
                                    <Button variant="outline" size="sm">
                                        <PaperclipIcon className="w-4 h-4 mr-2" />
                                        Attachments
                                    </Button>
                                </DialogTrigger>
                                <DialogContent className="w-[600px] font-poppins">
                                    <DialogHeader className="flex justify-between">
                                        <div>
                                            <DialogTitle>Attachments</DialogTitle>
                                            <CardDescription>These are all the files attached to this chat.</CardDescription>
                                        </div>
                                    </DialogHeader>
                                    <div className="space-y-2 mt-2">
                                        {isAttachmentLoading ? (
                                            <div className="flex items-center justify-center w-full h-full">
                                                <SpokeSpinner size='lg' color='var(--loader)' />
                                            </div>
                                        ) : (
                                            attachments.length > 0 ? (
                                                attachments.map((attachment, index) =>
                                                    renderDialogAttachment(attachment.fileType as FileType, attachment.fileName, attachment.fileUrl)
                                                )
                                            ) : (
                                                <div className="flex items-center justify-center w-full h-full">
                                                    <div className="text-gray-500 text-sm">No attachments found!</div>
                                                </div>
                                            )
                                        )}
                                    </div>
                                </DialogContent>
                            </Dialog>

                        </CardHeader>
                        <CardContent className="min-h-[29.8rem] max-h-[50vh] overflow-y-auto flex flex-col gap-4">
                            {loading ? (
                                <div className="flex items-center justify-center h-[29.8rem]">
                                    <SpokeSpinner size='xl' color='var(--loader)' />
                                </div>
                            ) : error ? (
                                <div>{error}</div>
                            ) : currentChat.length > 0 ? (
                                currentChat.map((chat, index) => (
                                    <div key={index} className="flex flex-col gap-2">
                                        {chat.file && renderChatAttachment(chat.fileType, chat.file, chat.fileName, chat.sender)}
                                        <div className={`flex ${chat.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                                            <div className={`p-3 rounded-lg max-w-[70%] ${chat.sender === 'user' ? 'bg-orange-400 text-white' : 'bg-gray-200 text-black'}`}>
                                                <div>{chat.message}</div>
                                            </div>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div>No chat history available.</div>
                            )}
                        </CardContent>

                    </Card>
                </div>
            </div>
        </div>
    );
}
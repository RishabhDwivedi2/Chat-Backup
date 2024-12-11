// src/components/custom/chat-bot/Preview.tsx

import React, { useEffect, useState } from 'react';
import { X, FileIcon } from 'lucide-react';
import { Button } from "./../../ui/button";
import { Dialog, DialogClose, DialogContent } from "./../../ui/dialog";
import { SpokeSpinner } from '@/components/ui/spinner';
import { ScrollArea } from '@/components/ui/scroll-area';
import { getBlob, ref } from 'firebase/storage';
import { storage } from '@/lib/firebase';

interface UploadedFile extends File {
  downloadUrl?: string;
  storagePath?: string;
  content?: string;
}

interface ImagePreviewProps {
  file: File;
  onRemove: () => void;
}

interface CustomFile extends File {
  downloadUrl?: string;
  storagePath?: string;
}

interface FilePreviewProps {
  file: UploadedFile;
  onRemove: () => void;
  isUploading: boolean;
}

const formatFileName = (fileName: string) => {
  const lastDotIndex = fileName.lastIndexOf('.');
  if (lastDotIndex === -1) return fileName;

  const name = fileName.substring(0, lastDotIndex);
  const extension = fileName.substring(lastDotIndex);

  if (name.length <= 10) return fileName;
  return `${name.substring(0, 8)}...${extension}`;
};

interface ImagePreviewProps {
  file: File;
  onRemove: () => void;
}

const ImagePreview: React.FC<ImagePreviewProps> = ({ file, onRemove }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <div className="relative group">
        <div className="relative w-20 h-20 cursor-pointer" onClick={() => setIsOpen(true)}>
          <img
            src={URL.createObjectURL(file)}
            alt={file.name}
            className="w-full h-full object-cover rounded-md"
          />

          <div className="absolute bottom-0 left-0 right-0 h-6 bg-black/60 rounded-b-md flex items-center justify-center">
            <span className="text-[10px] text-white px-1">
              {formatFileName(file.name)}
            </span>
          </div>
        </div>
        <Button
          variant="destructive"
          size="icon"
          className="absolute -top-2 -right-2 rounded-full w-6 h-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
        >
          <X className="h-3 w-3" />
        </Button>
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

const FilePreview: React.FC<FilePreviewProps> = ({ file, onRemove, isUploading }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [fileContent, setFileContent] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isTextFile = file.type === 'text/plain';

  const renderTextContent = () => {
    if (error) {
      return (
        <div className="text-center text-red-500 p-4">
          <p>{error}</p>
        </div>
      );
    }

    if (!file.content) {
      return (
        <div className="text-center text-gray-500 p-4">
          <p>No content available for preview</p>
        </div>
      );
    }

    return (
      <ScrollArea className="h-[60vh] w-full max-w-2xl rounded-md border p-4">
        <pre className="whitespace-pre-wrap font-mono text-sm">
          {file.content}
        </pre>
      </ScrollArea>
    );
  };

  const getFileTypeIcon = (file: File) => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'pdf':
        return <FileIcon className="w-10 h-10 text-red-500" />;
      case 'doc':
      case 'docx':
        return <FileIcon className="w-10 h-10 text-blue-500" />;
      case 'txt':
        return <FileIcon className="w-10 h-10 text-gray-500" />;
      default:
        return <FileIcon className="w-10 h-10 text-gray-500" />;
    }
  };

  return (
    <>
      <div className="relative group">
        <div
          className="relative w-20 h-20 flex items-center justify-center bg-[hsl(var(--accent))] rounded-md cursor-pointer"
          onClick={() => setIsOpen(true)}
        >
          {isUploading ? (
            <SpokeSpinner />
          ) : (
            getFileTypeIcon(file)
          )}

          <div className="absolute bottom-0 left-0 right-0 h-6 bg-black/60 rounded-b-md flex items-center justify-center">
            <span className="text-[10px] text-white px-1">
              {formatFileName(file.name)}
            </span>
          </div>
        </div>
        <Button
          variant="destructive"
          size="icon"
          className="absolute -top-2 -right-2 rounded-full w-6 h-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
        >
          <X className="h-3 w-3" />
        </Button>
      </div>

      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className={`sm:max-w-[90vw] sm:max-h-[90vh] w-full h-full flex flex-col items-center justify-center gap-4 ${isTextFile ? 'p-6' : ''}`}>
          <DialogClose className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground">
            <X className="h-4 w-4" />
            <span className="sr-only">Close</span>
          </DialogClose>

          <div className="flex flex-col items-center gap-2">
            {getFileTypeIcon(file)}
            <p className="text-sm font-medium">{file.name}</p>
          </div>

          {isTextFile && renderTextContent()}
        </DialogContent>
      </Dialog>
    </>
  );
};

export { ImagePreview, FilePreview };

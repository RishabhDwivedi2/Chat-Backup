// src/components/custom/chat-bot/FilePreview.tsx

import React, { useState } from 'react';
import { X, FileIcon } from 'lucide-react';
import { Button } from "./../../ui/button";
import { Dialog, DialogClose, DialogContent } from "./../../ui/dialog";

interface FilePreviewProps {
  file: File;
  onRemove: () => void;
  isUploading: boolean;
}

const FilePreview: React.FC<FilePreviewProps> = ({ file, onRemove }) => {
    const [isOpen, setIsOpen] = useState(false);
  
    const getFileTypeIcon = (file: File) => {
      const extension = file.name.split('.').pop()?.toLowerCase();
      switch (extension) {
        case 'pdf':
          return <FileIcon className="w-8 h-8 text-red-500" />;
        case 'doc':
        case 'docx':
          return <FileIcon className="w-8 h-8 text-blue-500" />;
        case 'txt':
          return <FileIcon className="w-8 h-8 text-gray-500" />;
        default:
          return <FileIcon className="w-8 h-8 text-gray-500" />;
      }
    };
  
    return (
      <>
        <div className="relative group">
          <div
            className="w-20 h-20 flex flex-col items-center justify-center bg-[hsl(var(--accent))] rounded-md cursor-pointer gap-1 p-1"
            onClick={() => setIsOpen(true)}
          >
            {getFileTypeIcon(file)}
            <span className="text-xs text-[hsl(var(--accent-foreground))] text-center truncate w-full">
              {file.name}
            </span>
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
          <DialogContent className="sm:max-w-[90vw] sm:max-h-[90vh] w-full h-full flex flex-col items-center justify-center gap-4">
            <DialogClose className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground">
              <X className="h-4 w-4" />
              <span className="sr-only">Close</span>
            </DialogClose>
            <div className="flex flex-col items-center gap-2">
              {getFileTypeIcon(file)}
              <p className="text-sm font-medium">{file.name}</p>
            </div>
          </DialogContent>
        </Dialog>
      </>
    );
  };
export default FilePreview;
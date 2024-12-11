// src/components/custom/chat-bot/ImagePreview.tsx

import React, { useState } from 'react';
import { X } from 'lucide-react';
import { Button } from "./../../ui/button";
import { Dialog, DialogClose, DialogContent } from "./../../ui/dialog";

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
          {/* Semi-transparent overlay with filename */}
          <div className="absolute inset-0 bg-black/40 rounded-md flex items-center justify-center p-1">
            <span className="text-xs text-white truncate max-w-full">
              {file.name}
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
  
  export default ImagePreview;
// src/utils/pasteValidator.ts

import { BlobCreatorHandler, FileSystemHandler, processLargeContent } from './contentHandlers';
import { toast } from '@/hooks/use-toast';
import { ToastAction } from '@/components/ui/toast';

interface ValidatorConfig {
  maxLength?: number;
  allowedFileTypes?: string[];
  maxFileSize?: number;
}

interface ValidationResult {
  isValid: boolean;
  content: string | null;
  shouldCreateFile: boolean;
  processedFile?: File;
  message?: {
    title: string;
    description: string;
  };
}

export class PasteValidator {
  private config: ValidatorConfig;

  constructor(config: ValidatorConfig = {}) {
    this.config = {
      maxLength: 1000,
      ...config
    };
  }

  private showToast(title: string, description: string, variant: "default" | "destructive" | null = "default") {
    toast({
      title,
      description,
      variant,
      className: `font-poppins`,
      action: <ToastAction altText="Okay">Okay</ToastAction>,
    });
  }

  public async validatePaste(
    clipboardData: DataTransfer,
    currentAttachments: number,
    uploadToFirebase: (file: File) => Promise<any>
  ): Promise<ValidationResult> {
    const textContent = clipboardData.getData('text');
    
    if (!textContent.trim()) {
      return {
        isValid: false,
        content: null,
        shouldCreateFile: false,
        message: {
          title: "Empty Content",
          description: "Cannot paste empty content."
        }
      };
    }

    if (textContent.length > this.config.maxLength!) {
      if (currentAttachments >= 5) {
        this.showToast(
          "Maximum Attachments Reached",
          "You can't add more attachments. Please remove some first.",
          "destructive"
        );
        return {
          isValid: false,
          content: null,
          shouldCreateFile: false,
        };
      }

      const result = await processLargeContent(
        textContent,
        currentAttachments,
        uploadToFirebase
      );

      if (!result.success) {
        this.showToast(
          "Processing Failed",
          result.error || "Failed to process content into file."
        );
        return {
          isValid: false,
          content: null,
          shouldCreateFile: false,
        };
      }

      return {
        isValid: false,
        content: textContent,
        shouldCreateFile: true,
        processedFile: result.file,
      };
    }

    return {
      isValid: true,
      content: textContent,
      shouldCreateFile: false
    };
  }
}

export const pasteValidator = new PasteValidator();
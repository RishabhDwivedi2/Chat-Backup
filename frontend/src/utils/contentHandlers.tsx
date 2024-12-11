// src/utils/contentHandlers.ts

interface BlobCreatorResult {
    blob: Blob;
    mimeType: string;
    size: number;
    content?: string;  
  }
  
  interface FileSystemResult {
    file: File & { content?: string };
    fileName: string;
  }
  
  export class BlobCreatorHandler {
    public createBlob(content: string): BlobCreatorResult {
      const blob = new Blob([content], { type: 'text/plain' });
      
      return {
        blob,
        mimeType: 'text/plain',
        size: blob.size,
        content  
      };
    }
  }
  
  export class FileSystemHandler {
    private generateFileName(): string {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      return `pasted-content-${timestamp}.txt`;
    }
  
    public createFile(blobData: BlobCreatorResult): FileSystemResult {
      const fileName = this.generateFileName();
      const file = new File([blobData.blob], fileName, {
        type: blobData.mimeType,
      }) as File & { content?: string };
  
      file.content = blobData.content;
  
      return {
        file,
        fileName
      };
    }
  }
  
  export const processLargeContent = async (
    content: string,
    currentAttachments: number,
    uploadToFirebase: (file: File) => Promise<any>
  ): Promise<{ success: boolean; error?: string; file?: File & { content?: string } }> => {
    try {
      if (currentAttachments >= 5) {
        return {
          success: false,
          error: "Maximum number of attachments (5) reached."
        };
      }
  
      const blobCreator = new BlobCreatorHandler();
      const blobResult = blobCreator.createBlob(content);
  
      const fileSystem = new FileSystemHandler();
      const { file } = fileSystem.createFile(blobResult);
  
      return {
        success: true,
        file
      };
    } catch (error) {
      return {
        success: false,
        error: "Failed to process content into file."
      };
    }
  };
// src/lib/minio.ts

const MINIO_ENDPOINT = 'http://localhost:9000';

// Utility function to generate URL for files
export const getFileUrl = (bucketName: string, objectName: string): string => {
    return `${MINIO_ENDPOINT}/${bucketName}/${objectName}`;
};

// Utility function to upload file
export const uploadFile = async (bucketName: string, file: File): Promise<{ downloadUrl: string; storagePath: string }> => {
    try {
        const timestamp = Date.now();
        const fileName = `${timestamp}-${file.name}`;
        const storagePath = fileName;

        const response = await fetch(`${MINIO_ENDPOINT}/${bucketName}/${storagePath}`, {
            method: 'PUT',
            headers: {
                'Content-Type': file.type,
            },
            body: file
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Upload error details:', errorText);
            throw new Error(`Upload failed: ${response.statusText}`);
        }

        const downloadUrl = getFileUrl(bucketName, storagePath);

        return {
            downloadUrl,
            storagePath
        };
    } catch (error) {
        console.error('Error uploading file:', error);
        throw error;
    }
};

// Utility function to delete file
export const deleteFile = async (bucketName: string, storagePath: string): Promise<void> => {
    try {
        const response = await fetch(`${MINIO_ENDPOINT}/${bucketName}/${storagePath}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error(`Delete failed: ${response.statusText}`);
        }
    } catch (error) {
        console.error('Error deleting file:', error);
        throw error;
    }
};
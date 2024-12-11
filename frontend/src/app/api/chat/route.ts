// src/app/api/chat/route.ts

import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

function cleanAuthToken(authHeader: string | null): string {
    if (!authHeader) return '';
    const token = authHeader.replace(/bearer/gi, '').trim();
    return token ? `Bearer ${token}` : '';
}

export async function POST(request: NextRequest) {
    try {
        const formData = await request.formData();
        const backendFormData = new FormData();
        
        // Log all incoming form data
        console.log('Incoming FormData:');
        for (const [key, value] of formData.entries()) {
            console.log(`${key}:`, value);
        }
        
        // Add basic fields
        backendFormData.append('prompt', formData.get('prompt')?.toString() || '');
        backendFormData.append('max_tokens', formData.get('max_tokens')?.toString() || '100');
        backendFormData.append('temperature', formData.get('temperature')?.toString() || '0.7');
        
        // Handle conversation_id
        const conversation_id = formData.get('conversation_id')?.toString();
        if (conversation_id && conversation_id !== 'null' && conversation_id !== 'undefined') {
            backendFormData.append('conversation_id', conversation_id);
        }
        
        // Handle attachments
        const attachments = formData.getAll('attachments');
        if (attachments.length > 0) {
            console.log('Forwarding attachments:', attachments);
            attachments.forEach((attachment) => {
                backendFormData.append('attachments', attachment);
            });
        }
        
        // Log what we're sending to the backend
        console.log('Sending to backend:');
        for (const [key, value] of backendFormData.entries()) {
            console.log(`${key}:`, value);
        }
        
        // Setup headers
        const rawAuthHeader = request.headers.get('Authorization');
        const headers = new Headers();
        headers.append('Authorization', cleanAuthToken(rawAuthHeader));
        
        // Log the request details
        console.log('Sending chat request:', {
            prompt: formData.get('prompt')?.toString()?.substring(0, 100) || '',
            hasConversationId: !!conversation_id,
            attachmentsCount: attachments.length
        });
        
        // Changed the endpoint from /api/chat to /api/gateway/web
        const backendUrl = new URL('/api/gateway/web', BACKEND_URL);
        const response = await fetch(backendUrl.toString(), {
            method: 'POST',
            headers,
            body: backendFormData
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            console.error('Backend error:', {
                status: response.status,
                error: error,
                authPresent: !!cleanAuthToken(rawAuthHeader)
            });
            
            // Special handling for 404 conversation not found
            if (response.status === 404 && error.detail === "Conversation not found") {
                // Remove the conversation ID from localStorage
                if (typeof window !== 'undefined') {
                    localStorage.removeItem('currentConversationId');
                }
            }
            
            return NextResponse.json(error, { status: response.status });
        }
        
        const data = await response.json();
        return NextResponse.json(data);
        
    } catch (error: any) {
        console.error("Error in chat API route:", error);
        return NextResponse.json(
            { error: "Failed to process chat request", details: error.message },
            { status: 500 }
        );
    }
}
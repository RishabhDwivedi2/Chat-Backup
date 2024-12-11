// src/app/api/chat-history/route.ts

import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
    try {
        // Get the authorization header from the incoming request
        const authHeader = request.headers.get('Authorization');
        
        if (!authHeader) {
            return NextResponse.json(
                { error: "No authorization token provided" }, 
                { status: 401 }
            );
        }

        // Forward the request to the backend
        const response = await fetch(`${BACKEND_URL}/api/chat/collections`, {
            headers: {
                'Authorization': authHeader,
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            
            // If conversation not found, clear from localStorage
            if (response.status === 404 && error.detail === "Conversation not found") {
                if (typeof window !== 'undefined') {
                    localStorage.removeItem('currentConversationId');
                }
            }
            
            return NextResponse.json(
                error, 
                { status: response.status }
            );
        }

        const data = await response.json();
        return NextResponse.json(data);

    } catch (error: any) {
        console.error("Error in chat-history route:", error);
        return NextResponse.json(
            { 
                error: "Failed to fetch chat history", 
                details: error.message 
            }, 
            { status: 500 }
        );
    }
}
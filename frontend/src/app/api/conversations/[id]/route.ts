// src/app/api/conversations/[id]/route.ts

import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

export async function GET(
    request: NextRequest,
    { params }: { params: { id: string } }
) {
    try {
        const conversationId = params.id;
        const authHeader = request.headers.get('Authorization');
        
        if (!authHeader) {
            return NextResponse.json(
                { error: "No authorization token provided" },
                { status: 401 }
            );
        }

        const response = await fetch(
            `${BACKEND_URL}/api/chat/conversations/${conversationId}`,
            {
                headers: {
                    'Authorization': authHeader,
                    'Content-Type': 'application/json',
                }
            }
        );

        if (!response.ok) {
            const error = await response.json();
            return NextResponse.json(error, { status: response.status });
        }

        const data = await response.json();
        return NextResponse.json(data);

    } catch (error: any) {
        console.error("Error fetching conversation:", error);
        return NextResponse.json(
            { error: "Failed to fetch conversation", details: error.message },
            { status: 500 }
        );
    }
}
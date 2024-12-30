// app/api/artifacts/[artifactId]/route.ts

import { NextRequest, NextResponse } from 'next/server';

interface ArtifactResponse {
    id: number;
    message_id: number;
    component_type: string;
    title: string;
    description: string | null;
    data: any;
    style: any | null;
    configuration: any | null;
    created_at: string;
    updated_at: string;
}

export async function GET(
    request: NextRequest,
    { params }: { params: { artifactId: string } }
) {
    try {
        // Get token from request headers
        const authHeader = request.headers.get('authorization');
        if (!authHeader) {
            return NextResponse.json(
                { error: 'Authorization header missing' },
                { status: 401 }
            );
        }

        // Extract artifact ID from params
        const { artifactId } = params;
        
        // Make request to backend API
        const response = await fetch(
            `http://localhost:8000/api/chat/artifacts/${artifactId}`,
            {
                method: 'GET',
                headers: {
                    'Authorization': authHeader,
                    'Content-Type': 'application/json',
                },
            }
        );

        // Handle different response statuses
        if (!response.ok) {
            const errorData = await response.json();
            if (response.status === 404) {
                return NextResponse.json(
                    { error: 'Artifact not found or unauthorized access' },
                    { status: 404 }
                );
            }
            if (response.status === 401) {
                return NextResponse.json(
                    { error: 'Unauthorized' },
                    { status: 401 }
                );
            }
            return NextResponse.json(
                { error: errorData.detail || 'Failed to fetch artifact details' },
                { status: response.status }
            );
        }

        // Parse and return successful response
        const artifactData: ArtifactResponse = await response.json();
        return NextResponse.json(artifactData);

    } catch (error) {
        console.error('Error fetching artifact details:', error);
        return NextResponse.json(
            { error: 'Internal server error' },
            { status: 500 }
        );
    }
}
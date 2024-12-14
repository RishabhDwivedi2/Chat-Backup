// app/api/proxy-image/route.ts

import { NextRequest, NextResponse } from 'next/server';
import { storage } from '@/lib/firebase';
import { getDownloadURL, ref } from 'firebase/storage';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const url = searchParams.get('url');
    
    if (!url) {
      return NextResponse.json({ error: 'URL is required' }, { status: 400 });
    }

    // Extract the path from Firebase Storage URL
    const pathMatch = url.match(/firebasestorage\.app\/(.+)$/);
    if (!pathMatch) {
      return NextResponse.json({ error: 'Invalid Firebase Storage URL' }, { status: 400 });
    }

    const storagePath = pathMatch[1];
    const storageRef = ref(storage, storagePath);

    try {
      // Get a fresh download URL
      const downloadUrl = await getDownloadURL(storageRef);

      // Fetch the image using the fresh URL
      const imageResponse = await fetch(downloadUrl);
      
      if (!imageResponse.ok) {
        throw new Error(`Failed to fetch image: ${imageResponse.statusText}`);
      }

      const contentType = imageResponse.headers.get('content-type');
      const arrayBuffer = await imageResponse.arrayBuffer();

      // Return the image with proper headers
      return new NextResponse(arrayBuffer, {
        headers: {
          'Content-Type': contentType || 'image/png',
          'Cache-Control': 'public, max-age=300',
          'Access-Control-Allow-Origin': '*',
        },
      });

    } catch (error) {
      console.error('Firebase storage error:', error);
      return NextResponse.json(
        { error: 'Failed to fetch from Firebase storage' },
        { status: 500 }
      );
    }

  } catch (error) {
    console.error('Error proxying image:', error);
    return NextResponse.json(
      { error: 'Failed to proxy image' },
      { status: 500 }
    );
  }
}

// Handle CORS preflight requests
export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}
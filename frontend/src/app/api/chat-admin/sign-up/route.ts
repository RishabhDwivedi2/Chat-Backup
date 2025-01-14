// /app/api/chat-admin/sign-up/route.ts

import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const signupData = await request.json();
    console.log("Route.ts received data:", signupData);

    const response = await fetch('http://localhost:8000/api/chat-admin/signup', {  
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(signupData),
    });

    console.log("Backend response status:", response.status);

    if (!response.ok) {
      const errorData = await response.json();
      console.error("Backend error:", errorData);
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log("Backend success response:", data);

    return NextResponse.json(data);
  } catch (error) {
    console.error('Route.ts error:', error);
    return NextResponse.json(
      { message: error instanceof Error ? error.message : 'Signup failed' }, 
      { status: error instanceof Error && error.message.includes('404') ? 404 : 400 }
    );
  }
}
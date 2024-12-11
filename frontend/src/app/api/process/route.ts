// File: src/app/api/process/route.ts
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { content, chatId } = await request.json();

    const response = await fetch('http://localhost:8000/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content, chat_id: chatId }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error:', error);
    return NextResponse.json({ message: 'Internal server error' }, { status: 500 });
  }
}
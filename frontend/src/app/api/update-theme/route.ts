// src/app/api/update-theme/route.ts

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const authorizationHeader = request.headers.get('authorization');
    const token = authorizationHeader ? authorizationHeader.split(' ')[1] : null;

    if (!token) {
      return NextResponse.json({ detail: 'Unauthorized' }, { status: 401 });
    }

    const body = await request.json();

    const response = await fetch('http://localhost:8000/api/users/me/theme', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(data, { status: response.status });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Error:', error);
    return NextResponse.json({ detail: 'Internal Server Error' }, { status: 500 });
  }
}

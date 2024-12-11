// File: src/app/api/test-auth/route.ts

import { NextResponse } from 'next/server';
import { getUserCount } from '@/lib/auth';

export async function GET() {
  try {
    const userCount = await getUserCount();
    return NextResponse.json({ success: true, userCount });
  } catch (error) {
    console.error('Error fetching user count:', error);
    return NextResponse.json({ success: false, error: 'Failed to fetch user count' }, { status: 500 });
  }
}

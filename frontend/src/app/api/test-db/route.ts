// File: src/app/api/test-db/route.ts

import { NextResponse } from 'next/server';
import { pool } from '@/lib/auth';

export async function GET() {
  try {
    const client = await pool.connect();
    try {
      const result = await client.query('SELECT NOW()');
      return NextResponse.json({ success: true, time: result.rows[0].now });
    } finally {
      client.release(); 
    }
  } catch (error) {
    console.error('Database connection error:', error);
    return NextResponse.json({ success: false, error: 'Database connection failed' }, { status: 500 });
  }
}

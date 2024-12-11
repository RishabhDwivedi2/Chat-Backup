// src/app/api/login/route.ts

import { NextResponse } from 'next/server';

type RoleCategory = 'Debtor' | 'FI Admin' | 'Resohub Admin' | 'Deltabots Admin' | string;

export async function POST(request: Request) {
  try {
    const { email, password } = await request.json();

    const response = await fetch('http://localhost:8000/api/users/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        username: email,
        password: password,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    const roleToProfile: Record<RoleCategory, string> = {
        'Debtor': 'Debtor',
        'FI Admin': 'FI Admin',
        'Resohub Admin': 'Resohub Admin',
        'Deltabots Admin': 'Deltabots Admin'
      };

    const profile = roleToProfile[data.user.role_category as RoleCategory] || data.user.role_category;

    console.log("Login successful. Profile set to:", profile);

    return NextResponse.json({
      ...data,
      profile: profile
    });
  } catch (error) {
    console.error('Error:', error);
    return NextResponse.json({ message: 'Login failed' }, { status: 401 });
  }
}
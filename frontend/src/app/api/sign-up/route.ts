// src/app/api/sign-up/route.ts

import { NextResponse } from 'next/server';

type RoleCategory = 'Debtor' | 'FI Admin' | 'Resohub Admin' | 'Deltabots Admin' | string;

export async function POST(request: Request) {
    try {
      const { name, email, password, confirm_password, role_category } = await request.json();
  
      if (!name || !email || !password || !confirm_password || !role_category) {
        return NextResponse.json({ message: "Missing required fields" }, { status: 400 });
      }
  
      const response = await fetch('http://localhost:8000/api/users/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name,
          email,
          password,
          confirm_password,
          role_category,
        }),
      });
  
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
  
      const data = await response.json();
  
      return NextResponse.json(data);
    } catch (error) {
      console.error('Error:', error);
      return NextResponse.json({ message: 'Signup failed' }, { status: 400 });
    }
  }
  
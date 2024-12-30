// src/components/custom/login/loginForm.tsx

'use client'

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import useProfileStore from '@/store/profileStore'
import { useTheme } from "next-themes"
import '@/app/globals.css'
import { removeThemeClasses, DEFAULT_THEME } from '@/config/themeConfig';

export function LoginForm() {
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState("")
    const router = useRouter()
    const { setProfile, setUserName, setColor, setMode } = useProfileStore()
    const { setTheme } = useTheme();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setError("")
        try {
            localStorage.removeItem('currentConversationId');

            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            });
    
            if (!response.ok) {
                throw new Error('Login failed');
            }
    
            const data = await response.json();
            
            console.log("Login response:", data);
    
            const token = data.access_token;
            localStorage.setItem('token', token);
        
            // Store user info
            localStorage.setItem('userId', data.user.id.toString());
            localStorage.setItem('userEmail', data.user.email);
            localStorage.setItem('userName', data.user.name); 
    
            // Existing Zustand state updates
            setProfile(data.user.role_category);
            setUserName(data.user.name);
            setColor(data.user.color);
            setMode(data.user.mode);
      
            removeThemeClasses(document.documentElement);
            document.documentElement.classList.add(DEFAULT_THEME.color.toLowerCase());
            document.documentElement.classList.add(DEFAULT_THEME.mode.toLowerCase());          

            console.log('Profile after login:', {
                profile: data.user.role_category,
                userName: data.user.name,
                color: data.user.color,
                mode: data.user.mode,
              });
            
            router.push('/');
        } catch (err) {
            setError("Invalid email or password");
        }
    }

    return (
        <div className="flex justify-center items-center h-screen font-poppins">
            <Card className="mx-auto max-w-sm">
                <CardHeader>
                    <CardTitle className="text-2xl">Login</CardTitle>
                    <CardDescription>
                        Enter your email below to login to your account
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="grid gap-4">
                        <div className="grid gap-2">
                            <Label htmlFor="email">Email</Label>
                            <Input
                                id="email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="m@example.com"
                                required
                            />
                        </div>
                        <div className="grid gap-2">
                            <div className="flex items-center">
                                <Label htmlFor="password">Password</Label>
                                <Link href="#" className="ml-auto inline-block text-sm underline">
                                    Forgot your password?
                                </Link>
                            </div>
                            <Input 
                                id="password" 
                                type="password" 
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required 
                            />
                        </div>
                        {error && <p className="text-red-500 text-sm">{error}</p>}
                        <Button type="submit" className="w-full">
                            Login
                        </Button>
                        <Button variant="outline" className="w-full">
                            Login with Google
                        </Button>
                    </form>
                    <div className="mt-4 text-center text-sm">
                        Don&apos;t have an account?{" "}
                        <Link href="/sign-up" className="underline">
                            Sign up
                        </Link>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
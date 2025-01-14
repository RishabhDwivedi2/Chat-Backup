// src/app/(pages)/admin/login/page.tsx

'use client'

import { LoginForm } from "@/components/custom/admin/login-form";

export default function LoginPage() {
    return <div className="min-h-screen w-full flex items-center justify-center p-4">
        <div className="w-full max-w-lg">
            <LoginForm />
        </div>
    </div>
}


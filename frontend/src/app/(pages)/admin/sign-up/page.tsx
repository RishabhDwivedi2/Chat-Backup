// src/app/(pages)/admin/sign-up/page.tsx

'use client'

import { SignupForm } from "@/components/custom/admin/sign-up-form";

export default function SignUpPage() {
    return <div className="min-h-screen w-full flex items-center justify-center p-4">
        <div className="w-full max-w-lg">
            <SignupForm />
        </div>
    </div>
}


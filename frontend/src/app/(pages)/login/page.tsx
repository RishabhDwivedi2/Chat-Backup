// src/app/(pages)/login/page.tsx

import { LoginForm } from "@/components/custom/login/loginForm"
import { Metadata } from 'next';

export const metadata: Metadata = {
    title: 'Login | Authentication',
};

export default function LoginPage() {
    return <LoginForm />
}
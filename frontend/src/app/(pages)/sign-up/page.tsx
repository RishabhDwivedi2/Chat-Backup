// src/app/(pages)/sign-up/page.tsx

import { SignUpForm } from "@/components/custom/sign-up/signUpForm"
import { Metadata } from 'next';

export const metadata: Metadata = {
    title: 'Sign Up | Authentication',
};

export default function SignUpPage() {
    return <SignUpForm />
}

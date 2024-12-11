// File: src/lib/auth-client.ts

import { createAuthClient } from "better-auth/react"

export const client = createAuthClient({
    baseURL: process.env.BETTER_AUTH_URL
})

export const { signIn, signUp, useSession } = client
'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import BreadcrumbComponent from '@/components/custom/bread-crumb'
import { SpokeSpinner } from "@/components/ui/spinner"
import { useToast } from "@/hooks/use-toast"
import { ToastAction } from "@/components/ui/toast"
import NavigationComponent from '@/components/custom/pg_navigation'
import HeaderComponent from '@/components/custom/pg_header'

export default function AddPrompt() {
    const [prompt, setPrompt] = useState("")
    const [error, setError] = useState(null)
    const [loading, setLoading] = useState(false)
    const { toast } = useToast()
    const textareaRef = useRef<HTMLTextAreaElement>(null)
    const router = useRouter()

    useEffect(() => {
        textareaRef.current?.focus()
    }, [])

    const handleSave = async () => {
        setLoading(true)
        setError(null)

        try {
            const response = await fetch("http://localhost:8000/create_prompt/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    prompt_text: prompt,
                }),
            })

            if (!response.ok) {
                throw new Error("Failed to save prompt")
            }

            const data = await response.json()
            console.log("Saved prompt:", data)

            toast({
                title: "Success",
                description: "Your prompt has been saved successfully!",
                action: <ToastAction altText="Close">Okay</ToastAction>,
            })
            setPrompt("")
            router.push('/all-prompts')
        } catch (err: any) {
            setError(err.message)

            toast({
                title: "Error",
                description: "Failed to save the prompt. Please try again.",
                variant: "destructive",
                action: <ToastAction altText="Close">Retry</ToastAction>,
            })
        } finally {
            setLoading(false)
        }
    }

    const handleClear = () => {
        setPrompt("")
    }

    return (
        <div className="grid h-screen w-full pl-[56px] font-poppins">
            <NavigationComponent defaultActive='main' />

            <div className="flex flex-col">
                <HeaderComponent />

                <BreadcrumbComponent
                    items={[
                        { label: 'Main', href: '/all-prompts' },
                        { label: 'All Prompts', href: '/all-prompts' }
                    ]}
                    separator=">"
                    currentPage="Add Prompt"
                />

                {/* Main Content */}
                <div className="flex flex-col items-center justify-center w-full h-full p-6">
                    <Card className="w-full max-w-full">
                        <CardHeader>
                            <CardTitle>Add Prompt</CardTitle>
                            <CardDescription>
                                Create a new prompt to be used in the chatbot.
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="flex flex-col gap-4">
                                <textarea
                                    ref={textareaRef}
                                    value={prompt}
                                    onChange={(e) => setPrompt(e.target.value)}
                                    className="w-full h-[26rem] p-4 border rounded-lg resize-y"
                                    placeholder="Enter your prompt here..."
                                    style={{ minHeight: "26rem" }}
                                    disabled={loading}
                                />
                                <div className="flex justify-end gap-4">
                                    <Button variant="secondary" onClick={handleClear} disabled={loading}>
                                        Clear
                                    </Button>
                                    <Button onClick={handleSave} disabled={!prompt || loading}>
                                        {loading ? (
                                            <div className="flex items-center">
                                                <SpokeSpinner /> Saving...
                                            </div>
                                        ) : "Save Prompt"}
                                    </Button>
                                </div>
                                {error && <p className="text-red-500">Error: {error}</p>}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    )
}

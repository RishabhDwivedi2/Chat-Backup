'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import BreadcrumbComponent from '@/components/custom/bread-crumb'
import { SpokeSpinner } from "@/components/ui/spinner"
import { useToast } from "@/hooks/use-toast"
import { ToastAction } from "@/components/ui/toast"
import FullPageLoader from '@/components/custom/page-loader'
import NavigationComponent from '@/components/custom/pg_navigation'
import HeaderComponent from '@/components/custom/pg_header'

export default function EditPrompt() {
    const { id } = useParams();
    const [prompt, setPrompt] = useState("");
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [saving, setSaving] = useState(false);
    const { toast } = useToast();

    useEffect(() => {
        const fetchPrompt = async () => {
            try {
                setIsLoading(true);
                const response = await fetch(`http://localhost:8000/get_specific_prompt/${id}`);
                if (!response.ok) {
                    throw new Error("Failed to fetch prompt data");
                }
                const data = await response.json();
                setPrompt(data.prompt_text);
            } catch (err: any) {
                setError(err.message);
            } finally {
                setIsLoading(false);
            }
        };
        fetchPrompt();
    }, [id]);

    const handleSave = async () => {
        setSaving(true);
        setError(null);

        try {
            const response = await fetch(`http://localhost:8000/update_prompt/${id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    prompt_text: prompt,
                }),
            });

            if (!response.ok) {
                throw new Error("Failed to update prompt");
            }

            const data = await response.json();
            console.log("Updated prompt:", data);

            toast({
                title: "Success",
                description: "Your prompt has been updated successfully!",
                action: <ToastAction altText="Close">Okay</ToastAction>,
            });
        } catch (err: any) {
            setError(err.message);

            toast({
                title: "Error",
                description: "Failed to update the prompt. Please try again.",
                variant: "destructive",
                action: <ToastAction altText="Close">Retry</ToastAction>,
            });
        } finally {
            setSaving(false);
        }
    };

    const handleClear = () => {
        setPrompt("");
    };

    if (isLoading) {
        return <FullPageLoader />;
    }

    if (error) {
        return <div>Error: {error}</div>;
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
                    currentPage="Edit Prompt"
                />

                {/* Main Content */}
                <div className="flex flex-col items-center justify-center w-full h-full p-6">
                    <Card className="w-full max-w-full">
                        <CardHeader>
                            <CardTitle>Edit Prompt</CardTitle>
                            <CardDescription>
                                Edit the prompt to be used in the chatbot.
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="flex flex-col gap-4">
                                <textarea
                                    value={prompt}
                                    onChange={(e) => setPrompt(e.target.value)}
                                    className="w-full h-[26rem] p-4 border rounded-lg resize-y"
                                    placeholder="Edit your prompt here..."
                                    style={{ minHeight: "26rem" }}
                                    disabled={saving}
                                />
                                <div className="flex justify-end gap-4">
                                    <Button variant="secondary" onClick={handleClear} disabled={saving}>
                                        Clear
                                    </Button>
                                    <Button onClick={handleSave} disabled={!prompt || saving}>
                                        {saving ? (
                                            <div className="flex items-center">
                                                <SpokeSpinner /> Updating...
                                            </div>
                                        ) : "Update Changes"}
                                    </Button>
                                </div>
                                {error && <p className="text-red-500">Error: {error}</p>}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}

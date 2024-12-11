// File: src/app/(pages)/settings/page.tsx

"use client"

import React, { useEffect, useState } from "react"
import Link from "next/link"
import { useRouter, usePathname } from "next/navigation"
import useProfileStore from "@/store/profileStore"
import { ChatHeader } from "@/components/custom/chat-bot/chat-header"
import { UserProfile } from "@/config/profileConfig"
import { TooltipProvider } from "@/components/ui/tooltip"
import DynamicProfilePanelRenderer from "@/components/custom/settings/render-panels"

const profileData = [
    { id: 'Debtor', name: 'Debtor' },
    { id: 'FI Admin', name: 'FI Admin' },
    { id: 'Resohub Admin', name: 'Resohub Admin' },
    { id: 'Deltabots Admin', name: 'Deltabots Admin' },
]

export default function SettingsPage() {
    const { profile } = useProfileStore()
    const router = useRouter()
    const pathname = usePathname()
    const [selectedProfile, setSelectedProfile] = useState<UserProfile>('Debtor')

    const [showAnimatedText, setShowAnimatedText] = useState(true)
    const [isChatHistoryActive, setIsChatHistoryActive] = useState(false)
    const [isChatArtifactsActive, setIsChatArtifactsActive] = useState(false)
    const [isChatProcessorActive, setIsChatProcessorActive] = useState(false)
    const [isChatControlsActive, setIsChatControlsActive] = useState(false)

    useEffect(() => {
        const pathParts = pathname.split('/')
        const profileFromPath = pathParts[pathParts.length - 1] as UserProfile
        if (profileData.some(p => p.id === profileFromPath)) {
            setSelectedProfile(profileFromPath)
        } else if (pathname === '/settings') {
            router.push('/settings/list-of-profiles/Debtor')
        }
    }, [pathname, router])

    const toggleChatControls = () => setIsChatControlsActive(!isChatControlsActive)
    const closeChatControls = () => setIsChatControlsActive(false)
    const toggleChatHistory = () => setIsChatHistoryActive(!isChatHistoryActive)
    const toggleChatArtifacts = () => setIsChatArtifactsActive(!isChatArtifactsActive)
    const toggleChatProcessor = () => setIsChatProcessorActive(!isChatProcessorActive)

    const handleLogout = () => {
        router.push("/set-up-profile")
    }

    const handleProfileSelect = (profileId: UserProfile) => {
        router.push(`/settings/list-of-profiles/${profileId}`)
    }

    const [isDrawerOpen, setIsDrawerOpen] = useState(false);

    const [isCoreRunning, setIsCoreRunning] = useState(false);

    const handleBackToWebsite = () => {
        router.push("http://localhost:3000");
    };
    const { userName, isHydrated, setIsHydrated } = useProfileStore();

    return (
        <TooltipProvider>
            <div className="flex min-h-screen w-full flex-col font-poppins settings-page">
                <ChatHeader
                    toggleChatControls={toggleChatControls}
                    closeChatControls={closeChatControls}
                    toggleChatHistory={toggleChatHistory}
                    toggleChatArtifacts={toggleChatArtifacts}
                    toggleChatProcessor={toggleChatProcessor}
                    showAnimatedText={showAnimatedText}
                    isChatHistoryActive={isChatHistoryActive}
                    isChatArtifactsActive={isChatArtifactsActive}
                    isChatProcessorActive={isChatProcessorActive}
                    isChatControlsActive={isChatControlsActive}
                    username={userName || "Guest"}
                    profile={profile as UserProfile}
                    onMoreDetails={() => setIsDrawerOpen(true)}
                    isCoreRunning={isCoreRunning}
                    onBackToWebsite={handleBackToWebsite}
                />
                <main className="flex min-h-[calc(100vh_-_theme(spacing.16))] flex-1 flex-col gap-4 bg-background p-4 md:gap-8 md:p-10">
                    <div className="mx-auto grid w-full max-w-6xl gap-2">
                        <h1 className="text-3xl font-semibold">Settings</h1>
                    </div>
                    <div className="mx-auto grid w-full max-w-6xl items-start gap-6 md:grid-cols-[180px_1fr] lg:grid-cols-[250px_1fr]">
                        <nav className="grid gap-4 text-sm text-muted-foreground">
                            <div>
                                <h2 className="font-semibold text-primary mb-2">List of Profiles</h2>
                                <ul className="ml-4 space-y-2">
                                    {profileData.map(({ id, name }) => (
                                        <li key={id}>
                                            <Link
                                                href={`/settings/list-of-profiles/${id}`}
                                                className={`${selectedProfile === id ? 'text-primary' : ''}`}
                                                onClick={(e) => {
                                                    e.preventDefault()
                                                    handleProfileSelect(id as UserProfile)
                                                }}
                                            >
                                                {name} ({id})
                                            </Link>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                            <Link href="#">Security</Link>
                            <Link href="#">Integrations</Link>
                            <Link href="#">Support</Link>
                            <Link href="#">Organizations</Link>
                            <Link href="#">Advanced</Link>
                        </nav>
                        <div className="grid gap-6">
                            <DynamicProfilePanelRenderer profile={selectedProfile} />
                        </div>
                    </div>
                </main>
            </div>
        </TooltipProvider>
    )
}
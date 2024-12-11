// File: src/app/(pages)/settings/list-of-profiles/[profileId]/page.tsx

'use client'

import React, { useEffect, useState } from "react"
import Link from "next/link"
import { useRouter, usePathname } from "next/navigation"
import useProfileStore from "@/store/profileStore"
import { ChatHeader } from "@/components/custom/chat-bot/chat-header"
import { UserProfile } from "@/config/profileConfig"
import { TooltipProvider } from "@/components/ui/tooltip"
import DynamicProfilePanelRenderer from "@/components/custom/settings/render-panels"
import { ChatHeaderMv } from "@/components/custom/chat-bot/mobile-view/chat-header-mv"
import { Button } from "@/components/ui/button"
import { MessageSquarePlus } from "lucide-react"
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet"

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

    const { userName, isHydrated, setIsHydrated } = useProfileStore();

    const [showAnimatedText, setShowAnimatedText] = useState(true)
    const [isChatHistoryActive, setIsChatHistoryActive] = useState(false)
    const [isChatArtifactsActive, setIsChatArtifactsActive] = useState(false)
    const [isChatProcessorActive, setIsChatProcessorActive] = useState(false)
    const [isChatControlsActive, setIsChatControlsActive] = useState(false)
    const [isDrawerOpen, setIsDrawerOpen] = useState(false);
    
    const [isMobile, setIsMobile] = useState(false)
    const [isSheetOpen, setIsSheetOpen] = useState(false)

    useEffect(() => {
        const pathParts = pathname.split('/')
        const profileFromPath = pathParts[pathParts.length - 1] as UserProfile
        if (profileData.some(p => p.id === profileFromPath)) {
            setSelectedProfile(profileFromPath)
        } else if (pathname === '/settings') {
            router.push('/settings/list-of-profiles/Debtor')
        }

        const checkMobile = () => setIsMobile(window.innerWidth < 600)
        checkMobile()
        window.addEventListener('resize', checkMobile)
        return () => window.removeEventListener('resize', checkMobile)
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
        setIsSheetOpen(false)
    }

    const handleMoreDetails = () => {
        setIsDrawerOpen(true);
    };

    const handleSettingsClick = () => {
        console.log("Settings clicked")
    }

    const handleNewChatClick = () => {
        router.push("/")
    }

    const toggleSheet = () => {
        setIsSheetOpen(!isSheetOpen)
    }

    const renderNewChatButton = () => (
        <Button variant="ghost" onClick={handleNewChatClick}>
            {isMobile ? (
                <MessageSquarePlus className="w-5 h-5" />
            ) : (
                <>
                    <MessageSquarePlus className="w-5 h-5 mr-2" />
                    New Chat
                </>
            )}
        </Button>
    )

    const [isCoreRunning, setIsCoreRunning] = useState(false);

    const handleBackToWebsite = () => {
        router.push("http://localhost:3000");
    };

    const commonHeaderProps = {
        toggleChatHistory,
        showAnimatedText,
        username: userName || "Guest",
        onLogout: handleLogout,
        profile: profile as UserProfile,
        onMoreDetails: handleMoreDetails,
        handleSettingsClick,
        isSettingsPage: true,
        renderNewChatButton,
    }

    const renderNavigation = () => (
        <nav className="grid gap-4 text-sm text-muted-foreground ">
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
                                {name}
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
    )

    return (
        <TooltipProvider>
            <div className="flex min-h-screen w-full flex-col font-poppins settings-page">
                {isMobile ? (
                    <>
                        <ChatHeaderMv {...commonHeaderProps} toggleMenu={toggleSheet} isCoreRunning={isCoreRunning} onBackToWebsite={handleBackToWebsite} />
                        <Sheet open={isSheetOpen} onOpenChange={setIsSheetOpen}>
                            <SheetContent side="left" className="w-[250px] sm:w-[300px]">
                                {renderNavigation()}
                            </SheetContent>
                        </Sheet>
                    </>
                ) : (
                    <ChatHeader
                        {...commonHeaderProps}
                        toggleChatControls={toggleChatControls}
                        closeChatControls={closeChatControls}
                        toggleChatArtifacts={toggleChatArtifacts}
                        toggleChatProcessor={toggleChatProcessor}
                        isChatHistoryActive={isChatHistoryActive}
                        isChatArtifactsActive={isChatArtifactsActive}
                        isChatProcessorActive={isChatProcessorActive}
                        isChatControlsActive={isChatControlsActive}
                        isCoreRunning={isCoreRunning}
                        onBackToWebsite={handleBackToWebsite}
                    />
                )}
                <main className="flex min-h-[calc(100vh_-_theme(spacing.16))] flex-1 flex-col gap-4 bg-background p-4 md:gap-8 md:p-10">
                    <div className="mx-auto grid w-full max-w-6xl gap-2">
                        <h1 className="text-3xl font-semibold">Settings</h1>
                    </div>
                    <div className="mx-auto grid w-full max-w-6xl items-start gap-6 md:grid-cols-[180px_1fr] lg:grid-cols-[250px_1fr]">
                        {!isMobile && renderNavigation()}
                        <div className="grid gap-6">
                            <DynamicProfilePanelRenderer profile={selectedProfile} />
                        </div>
                    </div>
                </main>
            </div>
        </TooltipProvider>
    )
}
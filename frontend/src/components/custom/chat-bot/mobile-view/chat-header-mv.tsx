import React from "react";
import { PanelLeftOpen, Settings2, UserCircle, LogOut, User, SunIcon, MoonIcon, LaptopIcon, Menu, ArrowLeft, DoorOpen, Minimize2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "next-themes";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuSub, DropdownMenuSubTrigger, DropdownMenuSubContent, DropdownMenuRadioGroup, DropdownMenuRadioItem } from "@/components/ui/dropdown-menu";
import { Tooltip, TooltipTrigger, TooltipContent } from "@/components/ui/tooltip";
import { UserProfile } from '@/config/profileConfig';
import AnimatedShinyText from "@/components/magicui/animated-shiny-text";
import useDynamicProfileConfigStore from "@/store/dynamicProfileConfigStore";

interface ChatHeaderMvProps {
    toggleChatHistory: () => void;
    showAnimatedText: boolean;
    username: string;
    onLogout: () => void;
    profile: UserProfile;
    onMoreDetails: () => void;
    handleSettingsClick: () => void;
    isSettingsPage: boolean;
    renderNewChatButton: () => React.ReactNode;
    toggleMenu: () => void;
    isCoreRunning: boolean;
    onBackToWebsite: () => void;
}

export const ChatHeaderMv: React.FC<ChatHeaderMvProps> = ({
    toggleChatHistory,
    showAnimatedText,
    username,
    onLogout,
    profile,
    onMoreDetails,
    handleSettingsClick,
    isSettingsPage,
    renderNewChatButton,
    toggleMenu,
    isCoreRunning,
    onBackToWebsite,
}) => {
    const { theme, setTheme } = useTheme();
    const { configs } = useDynamicProfileConfigStore();

    const isChatHistoryEnabled = configs[profile].headerPanels.includes('ChatHistory');

    return (
        <div className={`sticky top-0 z-10 bg-background flex justify-between h-[57px] ${isSettingsPage ? "px-4" : "px-0"} items-center w-full`}>
            <div className="flex items-center">
                {isSettingsPage ? (
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={toggleMenu}
                    >
                        <Menu className="w-5 h-5" />
                    </Button>
                ) : isChatHistoryEnabled ? (
                    <div className="flex items-center">
                        {isCoreRunning && (
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        onClick={onBackToWebsite}
                                    >
                                        <Minimize2 className="w-5 h-5" />
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent>
                                    <span>Back to Website</span>
                                </TooltipContent>
                            </Tooltip>
                        )}

                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={toggleChatHistory}
                                >
                                    <PanelLeftOpen className="w-5 h-5" />
                                </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                                <span>Chat History</span>
                            </TooltipContent>
                        </Tooltip>
                    </div>
                ) : <>
                    {isCoreRunning && (
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={onBackToWebsite}
                                >
                                    <Minimize2 className="w-5 h-5" />
                                </Button>
                            </TooltipTrigger>
                            <TooltipContent>
                                <span>Back to Website</span>
                            </TooltipContent>
                        </Tooltip>
                    )}
                </>}
            </div>
            <div className="flex-grow flex justify-center">
                {showAnimatedText && (
                    <AnimatedShinyText className="transition ease-out hover:text-muted-foreground cursor-pointer">
                        <span className="text-xl font-bold">✨ R. Chat</span>
                    </AnimatedShinyText>
                )}
            </div>
            <div className="flex items-center">
                {isSettingsPage ? renderNewChatButton() : null}
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                            <UserCircle className="w-5 h-5" />
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="min-w-[200px] font-poppins">
                        <DropdownMenuLabel className="flex items-center">
                            <User className="w-5 h-5 mr-2" />
                            {username} | {configs[profile].displayName}
                        </DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        {!isSettingsPage && (
                            <DropdownMenuItem onClick={onMoreDetails}>
                                <Settings2 className="w-4 h-4 mr-2" />
                                <span>More Details</span>
                            </DropdownMenuItem>
                        )}
                        <DropdownMenuSub>
                            <DropdownMenuSubTrigger>
                                <SunIcon className="w-4 h-4 mr-2" />
                                <span>Theme</span>
                            </DropdownMenuSubTrigger>
                            <DropdownMenuSubContent>
                                <DropdownMenuRadioGroup value={theme} onValueChange={setTheme}>
                                    <DropdownMenuRadioItem value="light">
                                        <SunIcon className="w-4 h-4 mr-2" />
                                        Light
                                    </DropdownMenuRadioItem>
                                    <DropdownMenuRadioItem value="dark">
                                        <MoonIcon className="w-4 h-4 mr-2" />
                                        Dark
                                    </DropdownMenuRadioItem>
                                    <DropdownMenuRadioItem value="system">
                                        <LaptopIcon className="w-4 h-4 mr-2" />
                                        System
                                    </DropdownMenuRadioItem>
                                </DropdownMenuRadioGroup>
                            </DropdownMenuSubContent>
                        </DropdownMenuSub>
                        {configs[profile].showSettings && !isSettingsPage && (
                            <DropdownMenuItem onClick={handleSettingsClick}>
                                <Settings2 className="w-4 h-4 mr-2" />
                                <span>Settings</span>
                            </DropdownMenuItem>
                        )}
                        {isCoreRunning && (
                            <DropdownMenuItem onClick={onBackToWebsite}>
                                <Minimize2 className="w-4 h-4 mr-2" />
                                <span>Back to Website</span>
                            </DropdownMenuItem>
                        )}
                        <DropdownMenuItem onClick={onLogout}>
                            <LogOut className="w-4 h-4 mr-2" />
                            <span>Log out</span>
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>
        </div>
    );
};
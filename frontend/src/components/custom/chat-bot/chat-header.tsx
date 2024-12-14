// File: src/components/custom/chat-bot/chat-header.tsx

import React, { useEffect, useState } from "react";
import { PanelLeftOpen, Settings2, ChartLine, Layers, UserCircle, LogOut, User, SunIcon, MoonIcon, LaptopIcon, Settings, MessageSquarePlus, Info, ArrowLeft, DoorOpen, Minimize2, Paintbrush, Check } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "next-themes";
import { useRouter, usePathname } from "next/navigation";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuSub, DropdownMenuSubTrigger, DropdownMenuSubContent, DropdownMenuRadioGroup, DropdownMenuRadioItem } from "@/components/ui/dropdown-menu";
import { Tooltip, TooltipTrigger, TooltipContent } from "@/components/ui/tooltip";
import { profileConfig, UserProfile, PanelType } from '@/config/profileConfig';
import AnimatedShinyText from "@/components/magicui/animated-shiny-text";
import useDynamicProfileConfigStore from "@/store/dynamicProfileConfigStore";
import { ChatHeaderMv } from "./mobile-view/chat-header-mv";
import { AnimatePresence, motion } from "framer-motion";
import useThemeStore from '@/store/themeStore';
import useProfileStore from "@/store/profileStore";
import { themeColors, themeModes, removeThemeClasses, DEFAULT_THEME } from '@/config/themeConfig';


interface ChatHeaderProps {
  toggleChatControls: () => void;
  closeChatControls: () => void;
  toggleChatHistory: () => void;
  toggleChatArtifacts: () => void;
  toggleChatProcessor: () => void;
  showAnimatedText: boolean;
  isChatHistoryActive: boolean;
  isChatArtifactsActive: boolean;
  isChatProcessorActive: boolean;
  isChatControlsActive: boolean;
  username: string;
  profile: UserProfile;
  onMoreDetails: () => void;
  isCoreRunning: boolean;
  onBackToWebsite: () => void;
}

const panelIcons: Record<PanelType, React.ReactNode> = {
  ChatControls: <Settings2 style={{ width: '18px', height: '18px' }} />,
  ChatArtifacts: <Layers style={{ width: '18px', height: '18px' }} />,
  ChatHistory: <PanelLeftOpen style={{ width: '18px', height: '18px' }} />,
  ChatProcessor: <ChartLine style={{ width: '18px', height: '18px' }} />,
  ChatContainer: null
};


const panelTooltips: Record<PanelType, string> = {
  ChatControls: "Chat Controls",
  ChatArtifacts: "Artifacts",
  ChatHistory: "Chat History",
  ChatProcessor: "Processor (For Analysis)",
  ChatContainer: "",
};

const orderedPanels: PanelType[] = ['ChatHistory', 'ChatProcessor', 'ChatControls', 'ChatArtifacts'];

export const ChatHeader: React.FC<ChatHeaderProps> = ({
  toggleChatControls,
  closeChatControls,
  toggleChatHistory,
  toggleChatArtifacts,
  toggleChatProcessor,
  showAnimatedText,
  isChatHistoryActive,
  isChatArtifactsActive,
  isChatProcessorActive,
  isChatControlsActive,
  username,
  profile,
  onMoreDetails,
  isCoreRunning,
  onBackToWebsite
}) => {
  const [mounted, setMounted] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const { theme, setTheme } = useTheme();
  const router = useRouter();
  const pathname = usePathname();
  const { configs } = useDynamicProfileConfigStore();

  useEffect(() => {
    setMounted(true);
    const checkMobile = () => setIsMobile(window.innerWidth < 600);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const handleSettingsClick = () => {
    router.push("/settings");
  };

  const handleNewChatClick = () => {
    router.push("/");
  };

  const toggleFunctions: Record<PanelType, () => void> = {
    ChatControls: toggleChatControls,
    ChatArtifacts: toggleChatArtifacts,
    ChatHistory: toggleChatHistory,
    ChatProcessor: toggleChatProcessor,
    ChatContainer: () => { }
  };

  const isActiveStates: Record<PanelType, boolean> = {
    ChatControls: isChatControlsActive,
    ChatArtifacts: isChatArtifactsActive,
    ChatHistory: isChatHistoryActive,
    ChatProcessor: isChatProcessorActive,
    ChatContainer: false
  };

  const handleMoreDetails = () => {
    onMoreDetails();
  };

  const handleToggleChatHistory = () => {
    // Trigger the chat history toggle
    toggleChatHistory();
  };

  const renderPanelButton = (panelName: PanelType) => {
    if (configs[profile] && configs[profile].headerPanels.includes(panelName)) {
      return (
        <Tooltip key={panelName}>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              onClick={panelName === 'ChatHistory' ? handleToggleChatHistory : toggleFunctions[panelName]}
              className={isActiveStates[panelName] ? "bg-accent text-accent-foreground" : ""}
            >
              {panelIcons[panelName]}
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <span>{panelTooltips[panelName]}</span>
          </TooltipContent>
        </Tooltip>
      );
    }
    return null;
  };

  const isSettingsPage = pathname.startsWith("/settings");

  const renderNewChatButton = () => (
    <Button variant="ghost" onClick={handleNewChatClick}>
      {
        isMobile ?
          <MessageSquarePlus className="w-5 h-5 mr-2" /> :
          <>
            <MessageSquarePlus className="w-5 h-5 mr-2" />
            New Chat
          </>
      }
    </Button>
  );

  const [isSheetOpen, setIsSheetOpen] = useState(false);

  const toggleMenu = () => {
    setIsSheetOpen(!isSheetOpen);
  };

  const { color, mode, setColor, setMode } = useProfileStore();

  useEffect(() => {
    applyTheme(color, mode);
    setTheme(mode);
  }, [color, mode, setTheme]);

  useEffect(() => {
    setMounted(true);
    const checkMobile = () => setIsMobile(window.innerWidth < 600);
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const applyTheme = (color: string, mode: string) => {
    removeThemeClasses(document.documentElement);
    document.documentElement.classList.add(color.toLowerCase());
    document.documentElement.classList.add(mode.toLowerCase());
  };

  const handleThemeChange = (newColor: string, newMode: string) => {
    setColor(newColor.toLowerCase());
    setMode(newMode.toLowerCase());

    const updateTheme = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          console.error('No token found');
          return;
        }

        const response = await fetch('/api/update-theme', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            color: newColor.toLowerCase(),
            mode: newMode.toLowerCase(),
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          console.error('Failed to update theme:', errorData.detail || response.statusText);
          setColor(color);
          setMode(mode);
        } else {
          const data = await response.json();
          console.log('Theme updated successfully:', data);
        }
      } catch (error) {
        console.error('Error updating theme:', error);
        setColor(color);
        setMode(mode);
      }
    };

    updateTheme();
  };

  const handleLogout = () => {
    const { setProfile, setUserName } = useProfileStore.getState();
  
    // Clear user profile data
    setProfile(null);
    setUserName("");
    setColor('zinc');
    setMode('light');
  
    // Clear localStorage
    localStorage.removeItem('user-profile-storage');
    localStorage.removeItem('currentConversationId'); 
    localStorage.removeItem('token');
  
    removeThemeClasses(document.documentElement);
    document.documentElement.classList.add(DEFAULT_THEME.color.toLowerCase());
    document.documentElement.classList.add(DEFAULT_THEME.mode.toLowerCase());  
  
    router.push("/login");
  };

  return (
    <header className="sticky top-0 z-10 flex h-[57px] items-center justify-between px-4 bg-background">
      {isMobile ? (
        <ChatHeaderMv
          toggleChatHistory={toggleChatHistory}
          showAnimatedText={showAnimatedText}
          username={username}
          onLogout={handleLogout}
          profile={profile}
          onMoreDetails={onMoreDetails}
          handleSettingsClick={handleSettingsClick}
          isSettingsPage={isSettingsPage}
          renderNewChatButton={renderNewChatButton}
          toggleMenu={toggleMenu}
          isCoreRunning={isCoreRunning}
          onBackToWebsite={onBackToWebsite}
        />
      ) : (
        <>
          <div className="flex items-center">
            {showAnimatedText && (
              <AnimatedShinyText
                className="inline-flex items-center justify-center mr-3 transition ease-out hover:text-neutral-600 hover:duration-300 hover:dark:text-neutral-400 cursor-pointer"
              >
                <span className="text-xl font-bold">✨ Chat.</span>
              </AnimatedShinyText>
            )}

            {isCoreRunning && showAnimatedText && (
              <AnimatePresence>
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.3 }}
                >
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={onBackToWebsite}
                        className="border border-border rounded-lg hover:bg-primary hover:text-primary-foreground transition-colors duration-200 w-7 h-7"
                      >
                        <Minimize2 className="w-4 h-4" />
                      </Button>
                    </TooltipTrigger>
                    <TooltipContent>
                      <span>Back to Website</span>
                    </TooltipContent>
                  </Tooltip>
                </motion.div>
              </AnimatePresence>
            )}
          </div>
          <div className="flex items-center gap-1">
            {isSettingsPage ? (
              renderNewChatButton()
            ) : (
              orderedPanels.map(panel => renderPanelButton(panel))
            )}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon">
                  <UserCircle style={{ width: '18px', height: '18px' }} />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="min-w-[200px] font-poppins">
                <DropdownMenuLabel className="flex items-center">
                  <User className="w-5 h-5 mr-2" />
                  {username} | {configs[profile] ? configs[profile].displayName : 'Unknown User'}
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuSub>
                  <DropdownMenuSubTrigger>
                    <Paintbrush className="w-4 h-4 mr-2" />
                    <span>Theme</span>
                  </DropdownMenuSubTrigger>
                  <DropdownMenuSubContent className="w-[350px]">
                    <div className="p-4">
                      <h3 className="text-sm font-medium mb-1">Customize</h3>
                      <p className="text-xs text-muted-foreground mb-4">Pick a color for your theme.</p>

                      <h4 className="text-sm font-medium mb-2">Color</h4>
                      <div className="grid grid-cols-3 gap-2 mb-4">
                        {themeColors.map((option) => (
                          <Button
                            key={option.name}
                            variant="outline"
                            size="sm"
                            className={`flex items-center justify-start gap-2 p-2 ${color.toLowerCase() === option.name.toLowerCase() ? 'ring-2 ring-primary' : ''}`}
                            onClick={() => handleThemeChange(option.name, mode)}
                          >
                            <div className="w-4 h-4 rounded-full relative flex items-center justify-center" style={{ backgroundColor: option.color }}>
                              {color.toLowerCase() === option.name.toLowerCase() && (
                                <Check className="w-3 h-3 text-white absolute" />
                              )}
                            </div>
                            <span className="text-xs">{option.name}</span>
                          </Button>
                        ))}
                      </div>

                      <h4 className="text-sm font-medium mb-2">Mode</h4>
                      <div className="flex gap-2">
                        {themeModes.map((themeMode) => (
                          <Button
                            key={themeMode}
                            variant={mode.toLowerCase() === themeMode.toLowerCase() ? "default" : "outline"}
                            size="sm"
                            onClick={() => handleThemeChange(color, themeMode)}
                            className="flex-1 justify-center"
                          >
                            {themeMode === "Light" ? <SunIcon className="w-4 h-4 mr-2" /> : <MoonIcon className="w-4 h-4 mr-2" />}
                            {themeMode}
                          </Button>
                        ))}
                      </div>
                    </div>
                  </DropdownMenuSubContent>
                </DropdownMenuSub>
                {configs[profile] && configs[profile].showSettings && (
                  <DropdownMenuItem onClick={handleSettingsClick}>
                    <Settings className="w-4 h-4 mr-2" />
                    <span>Settings</span>
                  </DropdownMenuItem>
                )}
                {isCoreRunning && (
                  <DropdownMenuItem onClick={onBackToWebsite}>
                    <Minimize2 className="w-4 h-4 mr-2" />
                    <span>Back to Website</span>
                  </DropdownMenuItem>
                )}
                <DropdownMenuItem onClick={handleLogout}>
                  <LogOut className="w-4 h-4 mr-2" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </>
      )}
    </header>
  );
};
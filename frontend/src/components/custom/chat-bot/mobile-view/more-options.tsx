import React, { useState, useEffect } from 'react';
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle, DrawerFooter } from "@/components/ui/drawer";
import { Button } from "@/components/ui/button";
import { DropdownMenu, DropdownMenuItem, DropdownMenuContent, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { MoreHorizontal } from "lucide-react";
import { UserProfile, PanelType } from "@/config/profileConfig";
import { ChatFontStyle } from '../panel-renderer';
import ChatControlsMv from './chat-controls-mv';
import ChatArtifactsMv from './chat-artifacts-mv';
import ChatProcessorMv from './chat-processor-mv';
import useDynamicProfileConfigStore from '@/store/dynamicProfileConfigStore';

type DrawerOption = 'Chat Controls' | 'Artifacts' | 'Processor';

interface Artifact {
    id: string;
    title: string;
    component: string;
    data: any;
    version: number;
    isLoading?: boolean;
}

interface MoreOptionsProps {
    isOpen: boolean;
    onOpenChange: (open: boolean) => void;
    defaultOption?: DrawerOption;
    profile: UserProfile;
    artifacts: any[];
    messages: any[];
    chatFontStyle: ChatFontStyle;
    onFontStyleChange: (newStyle: ChatFontStyle) => void;
    lastGeneratedArtifact: Artifact | null;
}

const panelToDrawerOption: Record<PanelType, DrawerOption> = {
    'ChatControls': 'Chat Controls',
    'ChatArtifacts': 'Artifacts',
    'ChatProcessor': 'Processor',
    'ChatHistory': 'Chat Controls',
    'ChatContainer': 'Chat Controls'
};

const MoreOptions: React.FC<MoreOptionsProps> = ({
    isOpen,
    onOpenChange,
    defaultOption = 'Chat Controls',
    profile,
    artifacts,
    messages,
    chatFontStyle,
    onFontStyleChange,
    lastGeneratedArtifact,
}) => {
    const { configs } = useDynamicProfileConfigStore();
    const [selectedDrawerOption, setSelectedDrawerOption] = useState<DrawerOption>(defaultOption);


    const enabledOptions = configs[profile]?.headerPanels
    ? configs[profile].headerPanels
        .map(panel => panelToDrawerOption[panel])
        .filter((option, index, self) => self.indexOf(option) === index) as DrawerOption[]
    : []; 


    const handleDrawerOptionChange = (option: DrawerOption) => {
        setSelectedDrawerOption(option);
    };

    const renderDrawerContent = () => {
        switch (selectedDrawerOption) {
            case 'Chat Controls':
                return (
                    <ChatControlsMv
                        profile={profile}
                        artifacts={artifacts}
                        attachments={messages.flatMap(message => message.files || [])}
                        chatFontStyle={chatFontStyle}
                        onFontStyleChange={onFontStyleChange}
                    />
                );
            case 'Artifacts':
                return (
                    <ChatArtifactsMv
                        artifact={lastGeneratedArtifact}
                        profile={profile}
                    />
                );
            case 'Processor':
                return <ChatProcessorMv />;
            default:
                console.log('No matching content for:', selectedDrawerOption);
                return null;
        }
    };

    return (
        <Drawer open={isOpen} onOpenChange={onOpenChange}>
            <DrawerContent className="font-poppins outline-none max-h-[85vh] flex flex-col">
                <DrawerHeader className="flex justify-between items-center">
                    <DrawerTitle>{selectedDrawerOption}</DrawerTitle>
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                                <MoreHorizontal className="h-4 w-4" />
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="font-poppins">
                            {enabledOptions.map((option) => (
                                <DropdownMenuItem
                                    key={option}
                                    onSelect={() => handleDrawerOptionChange(option)}
                                    className={selectedDrawerOption === option ? "bg-accent" : ""}
                                >
                                    <span>{option}</span>
                                </DropdownMenuItem>
                            ))}
                        </DropdownMenuContent>
                    </DropdownMenu>
                </DrawerHeader>
                <div className="flex-grow overflow-y-auto">
                    {renderDrawerContent()}
                </div>
                <DrawerFooter>
                    <Button onClick={() => onOpenChange(false)}>Close</Button>
                </DrawerFooter>
            </DrawerContent>
        </Drawer>
    );
};

export default MoreOptions;
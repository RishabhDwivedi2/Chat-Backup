// src/components/custom/chat-bot/chat-artifacts.tsx

import React, { useState, useEffect, useRef } from 'react';
import { ArrowRight, ChevronRight, ChevronsRight, Layers, X, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { SpokeSpinner } from "../../ui/spinner";
import DynamicComponent from '@/components/custom/chat-bot/dynamic-component';
import { UserProfile } from "@/config/profileConfig";
import {
    ArtifactItem,
    processNewArtifact,
    isArtifactDuplicate
} from '@/utils/artifactTransformer';

interface ChatArtifactsProps {
    onClose: () => void;
    onShowChatControls: () => void;
    className: string;
    artifactsData: { component: string, data: any, sub_type?: string } | null;
    profile: UserProfile;
}

const ChatArtifacts = ({
    onClose,
    onShowChatControls,
    className,
    artifactsData,
    profile
}: ChatArtifactsProps) => {
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const timer = setTimeout(() => {
            setLoading(false);
        }, 500);

        return () => clearTimeout(timer);
    }, []);

    const handleClose = () => {
        if (['Debtor', 'FI Admin', 'Resohub Admin'].includes(profile)) {
            onClose();
            onShowChatControls();
        } else {
            onClose();
        }
    };

    const renderContent = () => {
        if (artifactsData?.component === "loading") {
            return (
                <div className="flex flex-col items-center justify-center h-full">
                    <SpokeSpinner />
                    <p className="mt-4 text-muted-foreground">{artifactsData.data.title}</p>
                </div>
            );
        }
    
        if (artifactsData?.component === "error") {
            return (
                <div className="flex flex-col items-center justify-center h-full text-destructive">
                    <AlertCircle className="w-8 h-8 mb-2" />
                    <p className="text-md font-normal">{artifactsData.data.title}</p>
                    <p className="text-sm text-muted-foreground">{artifactsData.data.error}</p>
                </div>
            );
        }
    
        if (!artifactsData) {
            return (
                <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                    <p className="text-md font-normal">No artifact selected</p>
                </div>
            );
        }
    
        const constrainedData = {
            ...artifactsData,
            data: {
                ...artifactsData.data,
                style: {
                    ...artifactsData.data.style,
                    maxWidth: '100%',
                    maxHeight: '100%',
                    overflow: 'auto'
                }
            }
        };
    
        return (
            <div className="w-full h-full flex-1 overflow-hidden">
                <DynamicComponent
                    component={artifactsData.component.charAt(0).toUpperCase() + 
                             artifactsData.component.slice(1).toLowerCase() as "Table" | "Chart" | "Card" | "Text"}
                    data={constrainedData.data}
                    sub_type={artifactsData.sub_type}
                />
            </div>
        );
    };

    return (
        <div className="h-full flex flex-col rounded-lg border border-border bg-background">
            <div className="flex-none flex items-center justify-between p-4 border-b border-border">
                <div className="flex items-center gap-2">
                    <div className="p-2 bg-red-100 rounded-full">
                        <Layers className="w-5 h-5 text-red-500" />
                    </div>
                    <h2 className="text-md font-medium text-foreground">Artifacts</h2>
                </div>
                <Button
                    variant="ghost"
                    onClick={handleClose}
                    className="p-2 text-muted-foreground hover:text-foreground"
                >
                    <ChevronsRight className="w-5 h-5" />
                </Button>
            </div>
            <div className="flex-1 min-h-0 overflow-hidden p-2">
                {renderContent()}
            </div>
        </div>
    );
};

export default ChatArtifacts;
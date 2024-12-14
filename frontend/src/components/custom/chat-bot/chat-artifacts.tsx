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
    const [artifactList, setArtifactList] = useState<ArtifactItem[]>([]);
    const processedArtifacts = useRef(new Set<string>());

    useEffect(() => {
        const timer = setTimeout(() => {
            setLoading(false);
        }, 500);

        return () => clearTimeout(timer);
    }, []);

    useEffect(() => {
        if (!artifactsData) return;

        const artifactKey = JSON.stringify(artifactsData);

        if (!processedArtifacts.current.has(artifactKey)) {
            const newArtifact = processNewArtifact(artifactsData);

            if (newArtifact) {
                setArtifactList(prevArtifacts => {
                    if (!isArtifactDuplicate(newArtifact, prevArtifacts)) {
                        processedArtifacts.current.add(artifactKey);
                        return [newArtifact, ...prevArtifacts];
                    }
                    return prevArtifacts;
                });
            }
        }
    }, [artifactsData]);

    const handleClose = () => {
        if (['Debtor', 'FI Admin', 'Resohub Admin'].includes(profile)) {
            onClose();
            onShowChatControls();
        } else {
            onClose();
        }
    };

    const renderContent = () => {
        if (loading) {
            return (
                <div className="flex justify-center items-center h-full">
                    <SpokeSpinner />
                </div>
            );
        }

        if (artifactList.length === 0) {
            return (
                <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                    <AlertCircle className="w-12 h-12 mb-4" />
                    <p className="text-md font-normal">No artifacts found</p>
                </div>
            );
        }

        return artifactList.map((artifact, index) => (
            <div key={`${artifact.component}-${index}-${JSON.stringify(artifact.data)}`}>
                <DynamicComponent
                    component={artifact.component.charAt(0).toUpperCase() + artifact.component.slice(1).toLowerCase() as "Table" | "Chart" | "Card" | "Text"}
                    data={artifact.data}
                    sub_type={artifact.sub_type || undefined}
                />
            </div>
        ));
    };

    return (
        <div className={`h-full flex flex-col rounded-lg border border-border bg-background overflow-hidden sticky top-0`}>
            <div className="flex items-center justify-between p-4 border-b border-border">
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
            <div className="flex-grow overflow-y-auto overflow-x-hidden relative px-2 py-2">
                {renderContent()}
            </div>
        </div>
    );
};

export default ChatArtifacts;
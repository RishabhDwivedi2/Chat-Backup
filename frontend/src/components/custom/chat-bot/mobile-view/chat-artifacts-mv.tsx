// File: src/components/custom/chat-bot/mobile-view/chat-artifacts-mv.tsx

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertCircle } from 'lucide-react';
import DynamicComponent from '../dynamic-component';
import { UserProfile } from "@/config/profileConfig";

interface Artifact {
    id: string;
    title: string;
    component: string;
    data: any;
    version: number;
    isLoading?: boolean;
}

interface ChatArtifactsMvProps {
    artifact: Artifact | null;
    profile: UserProfile;
}

const ChatArtifactsMv: React.FC<ChatArtifactsMvProps> = ({ artifact, profile }) => {
    if (!artifact) {
        return (
            <div className="flex-grow overflow-y-auto overflow-x-hidden relative px-2 py-2">
                <div className="flex flex-col items-center justify-center border border-border my-4 rounded-md text-center p-4 text-muted-foreground">
                    <AlertCircle className="w-12 h-12 mb-4" />
                    <h3 className="text-md font-medium mb-2">No artifacts generated yet</h3>
                    <p className="text-sm">
                        Generate the artifacts via your request.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="p-4">
            <Card className="dynamic-card mb-4">
                <CardHeader>
                    <CardTitle>{artifact.title || 'Dynamic Component'}</CardTitle>
                </CardHeader>
                <CardContent>
                    <DynamicComponent
                        component={artifact.component as "Table" | "Chart" | "Card" | "Text"}
                        data={artifact.data}
                    />
                </CardContent>
            </Card>
        </div>
    );
};

export default ChatArtifactsMv;
// File: src/components/custom/chat-bot/mobile-view/chat-controls-mv.tsx

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { CodeXml, FileText } from 'lucide-react';
import { ChatFontStyle } from '../panel-renderer';
import { hasMinimumProfileLevel } from '@/utils/hasAccessToPanel';
import { UserProfile } from "@/config/profileConfig";

interface ChatControlsMvProps {
    profile: UserProfile;
    artifacts: any[];
    attachments: File[];
    chatFontStyle: ChatFontStyle;
    onFontStyleChange: (newStyle: ChatFontStyle) => void;
}

const ChatControlsMv: React.FC<ChatControlsMvProps> = ({
    profile,
    artifacts,
    attachments,
    chatFontStyle,
    onFontStyleChange
}) => {
    const canAccessArtifacts = hasMinimumProfileLevel(profile, 2);

    const handleArtifactClick = (artifactId: string) => {
        if (canAccessArtifacts) {
            console.log("Artifact clicked:", artifactId);
        } else {
            console.log("Artifact clicked, but ChatArtifacts not available for this profile");
        }
    };

    const hasContent = artifacts.length > 0 || attachments.length > 0;

    return (
        <div className="flex-grow overflow-y-auto overflow-x-hidden relative px-2 py-2">
            {!hasContent ? (
                <div className="flex flex-col items-center justify-center border border-border my-4 rounded-md text-center p-4 text-muted-foreground">
                    <h3 className="text-md font-medium mb-2">No content added yet</h3>
                    <p className="text-sm">
                        Add images, PDFs, docs, spreadsheets, and more to summarize,
                        analyze, and query content with Claude.
                    </p>
                </div>
            ) : (
                <>
                    {artifacts.length > 0 && (
                        <div className="w-full mb-6 mt-1">
                            <h4 className="text-sm font-small mb-2 text-foreground">Artifacts</h4>
                            {artifacts.map((artifact) => (
                                <Card key={artifact.id} onClick={() => handleArtifactClick(artifact.id)} className="mb-2">
                                    <CardContent className="flex items-center gap-4 p-4 cursor-pointer">
                                        <div className="p-2 bg-secondary rounded">
                                            <CodeXml className="w-6 h-6 text-secondary-foreground" />
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-foreground">{artifact.title}</p>
                                            <p className="text-xs text-muted-foreground">
                                                {canAccessArtifacts ? 'Click to open component' : 'Artifact view not available'} • {artifact.version} version(s)
                                            </p>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    )}

                    {attachments.length > 0 && (
                        <div className="w-full mb-6">
                            <h4 className="text-sm font-small mb-2 text-foreground">Attachments</h4>
                            {attachments.map((file, index) => (
                                <Card key={index} className="mb-2">
                                    <CardContent className="flex items-center gap-4 p-4 cursor-pointer">
                                        <div className="p-2 bg-primary rounded">
                                            <FileText className="w-6 h-6 text-primary-foreground" />
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-foreground">{file.name}</p>
                                            <p className="text-xs text-muted-foreground">{(file.size / 1024).toFixed(2)} KB</p>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    )}
                </>
            )}

            <div className="w-full mb-6">
                <h4 className="text-sm font-small mb-2 text-foreground">Chat styles</h4>
                <Card>
                    <CardContent className="flex items-center justify-between p-4">
                        <span className="text-sm text-foreground">Aa</span>
                        <Select value={chatFontStyle} onValueChange={(value: ChatFontStyle) => onFontStyleChange(value)}>
                            <SelectTrigger className="w-[180px] border bg-background text-foreground">
                                <SelectValue placeholder="Font" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="Default">Default</SelectItem>
                                <SelectItem value="Match System">Match System</SelectItem>
                                <SelectItem value="Dyslexic friendly">Dyslexic friendly</SelectItem>
                            </SelectContent>
                        </Select>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default ChatControlsMv;
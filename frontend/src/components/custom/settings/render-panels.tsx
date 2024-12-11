// File: src/components/custom/settings/render-panels.tsx

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { UserProfile, PanelType } from '@/config/profileConfig';
import useDynamicProfileConfigStore from '@/store/dynamicProfileConfigStore';
import { toast } from '@/hooks/use-toast';
import { User2, Landmark, Briefcase, UserCog } from 'lucide-react';

interface RenderPanelProps {
    profile: UserProfile;
}

const profileIcons = {
    Debtor: User2,
    'FI Admin': Landmark,
    'Resohub Admin': Briefcase,
    'Deltabots Admin': UserCog,
};

const profileData = [
    { id: 'Debtor', name: 'Debtor' },
    { id: 'FI Admin', name: 'FI Admin' },
    { id: 'Resohub Admin', name: 'Resohub Admin' },
    { id: 'Deltabots Admin', name: 'Deltabots Admin' },
];

const DynamicProfilePanelRenderer: React.FC<RenderPanelProps> = ({ profile }) => {
    const { configs, updateConfig, resetToDefault, saveChanges, getConfigSource, setConfigSource } = useDynamicProfileConfigStore();
    const [localConfig, setLocalConfig] = useState(configs[profile]);
    const [hasChanges, setHasChanges] = useState(false);
    const [selectedConfigProfile, setSelectedConfigProfile] = useState<UserProfile>(getConfigSource(profile));
    const [isMobile, setIsMobile] = useState(false);

    useEffect(() => {
        const checkMobile = () => {
            setIsMobile(window.innerWidth < 768);
        };
        checkMobile();
        window.addEventListener('resize', checkMobile);
        return () => window.removeEventListener('resize', checkMobile);
    }, []);

    useEffect(() => {
        setLocalConfig(configs[profile]);
        setSelectedConfigProfile(getConfigSource(profile));
    }, [configs, profile, getConfigSource]);

    useEffect(() => {
        setHasChanges(JSON.stringify(localConfig) !== JSON.stringify(configs[profile]));
    }, [localConfig, configs, profile]);

    const handlePanelToggle = (panel: PanelType) => {
        setLocalConfig(prevConfig => ({
            ...prevConfig,
            panels: prevConfig.panels.includes(panel)
                ? prevConfig.panels.filter(p => p !== panel)
                : [...prevConfig.panels, panel]
        }));
    };

    const handleHeaderPanelToggle = (panel: PanelType) => {
        setLocalConfig(prevConfig => ({
            ...prevConfig,
            headerPanels: prevConfig.headerPanels.includes(panel)
                ? prevConfig.headerPanels.filter(p => p !== panel)
                : [...prevConfig.headerPanels, panel]
        }));
    };

    const handleMaxPanelsChange = (value: number) => {
        setLocalConfig(prevConfig => ({
            ...prevConfig,
            maxPanels: value
        }));
    };

    const handleDisplayNameChange = (value: string) => {
        setLocalConfig(prevConfig => ({
            ...prevConfig,
            displayName: value
        }));
    };

    const handleShowSettingsToggle = () => {
        setLocalConfig(prevConfig => ({
            ...prevConfig,
            showSettings: !prevConfig.showSettings
        }));
    };

    const handleSaveChanges = () => {
        updateConfig(profile, localConfig);
        setConfigSource(profile, selectedConfigProfile);
        saveChanges();
        setHasChanges(false);
        toast({
            title: "Changes Saved",
            description: `Your ${configs[profile].displayName} configuration changes have been saved.`,
            className: "bg-green-500 font-poppins text-white",
        });
    };

    const handleResetToDefault = () => {
        resetToDefault();
        setLocalConfig(configs[profile]);
        setSelectedConfigProfile(profile);
        setConfigSource(profile, profile);
        setHasChanges(false);
        toast({
            title: "Reset to Default",
            description: `Your ${configs[profile].displayName} configurations have been reset to their default values.`,
            className: "font-poppins",
        });
    };

    const handleProfileConfigSelect = (selectedProfile: UserProfile) => {
        setSelectedConfigProfile(selectedProfile);
        const selectedConfig = configs[selectedProfile];
        setLocalConfig(prevConfig => ({
            ...selectedConfig,
            displayName: prevConfig.displayName, 
        }));
    };

    const Icon = profileIcons[profile];

    return (
        <Card className="w-full">
            <CardHeader>
                <div className={`flex ${isMobile ? 'flex-col' : 'flex-row'} items-start justify-between space-y-2 sm:space-y-0 sm:items-center`}>
                    <div className="flex items-center space-x-2">
                        <Icon className="h-6 w-6" />
                        <CardTitle className="text-lg">{configs[profile].displayName} Configurations</CardTitle>
                    </div>
                    <Select
                        value={selectedConfigProfile}
                        onValueChange={(value) => handleProfileConfigSelect(value as UserProfile)}
                    >
                        <SelectTrigger className={`${isMobile ? 'w-full' : 'w-[180px]'}`}>
                            <SelectValue placeholder="Select profile config" />
                        </SelectTrigger>
                        <SelectContent>
                            {profileData.map(({ id, name }) => (
                                <SelectItem key={id} value={id}>{name}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
            </CardHeader>
            <CardContent>
                <div className="space-y-6">
                    <div className="space-y-2">
                        <Label htmlFor={`${profile}-display-name`} className='text-sm font-semibold'>Display Name</Label>
                        <Input
                            id={`${profile}-display-name`}
                            value={localConfig.displayName}
                            onChange={(e) => handleDisplayNameChange(e.target.value)}
                            className="w-full"
                        />
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor={`${profile}-max-panels`} className='text-sm font-semibold'>Max Panels</Label>
                        <Input
                            id={`${profile}-max-panels`}
                            type="number"
                            value={localConfig.maxPanels}
                            onChange={(e) => handleMaxPanelsChange(parseInt(e.target.value))}
                            className="w-full"
                        />
                    </div>
                    <div className="space-y-2">
                        <Label className='text-sm font-semibold'>Panels</Label>
                        <div className={`grid ${isMobile ? 'grid-cols-1' : 'grid-cols-2'} gap-4`}>
                            {['ChatContainer', 'ChatControls', 'ChatArtifacts', 'ChatHistory', 'ChatProcessor'].map((panel) => (
                                <div key={panel} className="flex items-center space-x-2">
                                    <Checkbox
                                        id={`${profile}-${panel}`}
                                        checked={localConfig.panels.includes(panel as PanelType)}
                                        onCheckedChange={() => handlePanelToggle(panel as PanelType)}
                                    />
                                    <label htmlFor={`${profile}-${panel}`} className="text-sm">{panel}</label>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div className="space-y-2">
                        <Label className='text-sm font-semibold'>Header Panels</Label>
                        <div className={`grid ${isMobile ? 'grid-cols-1' : 'grid-cols-2'} gap-4`}>
                            {['ChatControls', 'ChatArtifacts', 'ChatHistory', 'ChatProcessor'].map((panel) => (
                                <div key={panel} className="flex items-center space-x-2">
                                    <Checkbox
                                        id={`${profile}-header-${panel}`}
                                        checked={localConfig.headerPanels.includes(panel as PanelType)}
                                        onCheckedChange={() => handleHeaderPanelToggle(panel as PanelType)}
                                    />
                                    <label htmlFor={`${profile}-header-${panel}`} className="text-sm">{panel}</label>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div className="flex items-center space-x-2">
                        <Switch
                            id={`${profile}-show-settings`}
                            checked={localConfig.showSettings}
                            onCheckedChange={handleShowSettingsToggle}
                        />
                        <Label htmlFor={`${profile}-show-settings`}>Show Settings</Label>
                    </div>
                </div>
                <div className={`flex ${isMobile ? 'flex-col' : 'flex-row'} justify-between mt-6 space-y-2 sm:space-y-0`}>
                    <Button
                        onClick={handleResetToDefault}
                        variant="outline"
                        className={`${isMobile ? 'w-full' : 'w-auto'}`}
                    >
                        Reset to Default
                    </Button>
                    <Button
                        onClick={handleSaveChanges}
                        disabled={!hasChanges}
                        className={`${isMobile ? 'w-full' : 'w-auto'}`}
                    >
                        Save Changes
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
};

export default DynamicProfilePanelRenderer;
// ArtifactsTab.tsx
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { CodeXml } from 'lucide-react';

const ArtifactsTab: React.FC = () => {
    return (
        <Card>
            <CardContent className="flex items-center gap-4 p-4 cursor-pointer">
                <div className="p-2 bg-gray-700 rounded">
                    <CodeXml className="w-6 h-6 text-white" />
                </div>
                <div>
                    <p className="text-sm font-medium">Debt Settlement Agreement Summary</p>
                    <p className="text-xs">Click to open component • 1 version</p>
                </div>
            </CardContent>
        </Card>
    );
}

export default ArtifactsTab;
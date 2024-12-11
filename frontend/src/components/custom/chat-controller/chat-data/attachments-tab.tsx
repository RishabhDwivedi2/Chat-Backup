// AttachmentsTab.tsx
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { FileText } from 'lucide-react';

const AttachmentsTab: React.FC = () => {
    return (
        <Card>
            <CardContent className="flex items-center gap-4 p-4 cursor-pointer">
                <div className="p-2 bg-violet-500 rounded">
                    <FileText className="w-6 h-6 text-white" />
                </div>
                <div>
                    <p className="text-sm font-medium">Document 1.docx</p>
                    <p className="text-xs">35.15 KB</p>
                </div>
            </CardContent>
        </Card>
    );
}

export default AttachmentsTab;
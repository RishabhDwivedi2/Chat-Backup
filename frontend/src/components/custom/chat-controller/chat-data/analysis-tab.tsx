'use client';

import React, { useEffect } from 'react';
import { useAnalysisStore } from '@/store/analysisStore';
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "@/components/ui/accordion";
import { Card } from "@/components/ui/card";
import { BarChart3, Check, RefreshCw } from 'lucide-react';
import { SpokeSpinner } from '@/components/ui/spinner';
import { Button } from '@/components/ui/button';

const AnalysisTab: React.FC = () => {
    const { analyses, refreshAnalyses } = useAnalysisStore();

    useEffect(() => {
        console.log("AnalysisTab: Analyses updated", analyses);
    }, [analyses]);

    const handleRefresh = () => {
        refreshAnalyses();
    };

    const renderStatus = (status: string) => {
        switch (status) {
            case 'completed':
                return <Check className="w-5 h-5 text-green-500" />;
            case 'inProgress':
                return <SpokeSpinner />;
            default:
                return <span className="w-5 h-5" />;
        }
    };

    if (analyses.length === 0) {
        return <div className="p-4">No analyses available</div>;
    }

    return (
        <div className="relative h-full flex flex-col overflow-hidden py-2" >
            <div className="flex-grow overflow-y-auto px-2 py-4" style={{ scrollbarGutter: 'stable', maxHeight: '500px' }}>
                <Accordion type="single" collapsible className="w-full space-y-2">
                    {analyses.map((analysis) => (
                        <AccordionItem key={analysis.id} value={analysis.id} className="border-0">
                            <Card className="w-full">
                                <AccordionTrigger className="hover:no-underline w-full px-4 py-4">
                                    <div className="flex items-center justify-between w-full">
                                        <div className="flex items-center gap-4">
                                            <div className="p-2 bg-green-100 rounded-full">
                                                <BarChart3 className="w-6 h-6 text-green-500" />
                                            </div>
                                            <div className="text-left">
                                                <p className="text-sm font-medium">{analysis.title}</p>
                                                <p className="text-xs text-muted-foreground">{analysis.subtext}</p>
                                            </div>
                                        </div>
                                    </div>
                                </AccordionTrigger>
                                <AccordionContent>
                                    <div className="px-4 pb-4">
                                        <div className="space-y-2 pl-14">
                                            {analysis.steps.map((step, index) => (
                                                <div key={index} className="flex justify-between items-center text-sm">
                                                    <span className="flex items-center gap-2">
                                                        {renderStatus(step.status)}
                                                        {step.name}
                                                    </span>
                                                    <span className={step.status === 'completed' ? 'text-green-500' : 'text-gray-500'}>
                                                        {step.status === 'completed' ? step.duration : '-'}
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                        {analysis.agent1Response && (
                                            <div className="mt-4 p-3 bg-blue-50 rounded-md">
                                                <p className="text-sm font-medium text-blue-700">Agent 1 Response:</p>
                                                <pre className="text-sm text-blue-600 whitespace-pre-wrap">{JSON.stringify(analysis.agent1Response, null, 2)}</pre>
                                            </div>
                                        )}
                                        {analysis.agent2Response && (
                                            <div className="mt-4 p-3 bg-green-50 rounded-md">
                                                <p className="text-sm font-medium text-green-700">Agent 2 Response:</p>
                                                <pre className="text-sm text-green-600 whitespace-pre-wrap">{JSON.stringify(analysis.agent2Response, null, 2)}</pre>
                                            </div>
                                        )}
                                    </div>
                                </AccordionContent>
                            </Card>
                        </AccordionItem>
                    ))}
                </Accordion>
            </div>
            <div className="absolute bottom-10 right-1">
                <Button
                    className="rounded-full w-12 h-12 flex items-center justify-center bg-blue-500 text-white hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                    onClick={handleRefresh}
                    aria-label="Refresh analyses"
                >
                    <RefreshCw className="w-6 h-6" />
                </Button>
            </div>
        </div>
    );
};

export default AnalysisTab;
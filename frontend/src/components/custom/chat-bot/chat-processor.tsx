// File: src/components/custom/chat-bot/chat-processor.tsx

import React, { useEffect, useState } from 'react';
import { useProcessorStore } from "@/store/processorStore";
import { ChevronsRight, ChartLine, RadioTower } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { SpokeSpinner } from "@/components/ui/spinner";
import { Check } from 'lucide-react';

interface AgentResponse {
    content: string;
    component?: string;
    chartType?: string;
    style?: {
        innerRadius?: string;
        outerRadius?: string;
        barColors?: string[];
        backgroundColor?: string;
    };
}

interface ChatProcessorProps {
    className: string;
    onClose: () => void;
}

const AgentResponseRenderer: React.FC<{ response: AgentResponse, title: string, bgColor: string }> = ({ response, title, bgColor }) => {
    return (
        <div className={`p-3 ${bgColor} rounded-md`}>
            <p className={`text-sm font-thin mb-3 ${bgColor.replace('bg-', 'text-').replace('-50', '-700')}`}>{title}</p>
            <code className="text-xs mt-[50px]">{JSON.stringify(response, null, 2)}</code>
        </div>
    );
};

export default function ChatProcessor({ className, onClose }: ChatProcessorProps) {
    const { analyses, refreshAnalyses } = useProcessorStore();
    const [openAccordion, setOpenAccordion] = useState<string | null>(null);

    useEffect(() => {
        refreshAnalyses();
    }, [refreshAnalyses]);

    useEffect(() => {
        if (analyses.length > 0) {
            setOpenAccordion(analyses[0].id);
        }
    }, [analyses]);

    const renderStatus = (step: { status: string; name: string; duration?: string }) => {
        switch (step.status) {
            case 'completed':
                return <Check className="w-5 h-5 text-green-500" />;
            case 'inProgress':
                return <SpokeSpinner />;
            default:
                return <span className="w-5 h-5" />;
        }
    };

    return (
        <div className={`h-full flex flex-col rounded-lg border border-border bg-background overflow-hidden sticky top-0`}>
            <div className="flex items-center justify-between p-4 border-b border-border">
                <div className="flex items-center gap-2">
                    <div className="p-2 bg-green-100 rounded-full">
                        <ChartLine className="w-5 h-5 text-green-500" />
                    </div>
                    <h2 className="text-md font-medium text-foreground">Processor</h2>
                </div>
                <Button
                    variant="ghost"
                    onClick={onClose}
                    className="p-2 text-muted-foreground hover:text-foreground"
                >
                    <ChevronsRight className="w-5 h-5" />
                </Button>
            </div>

            <div className="flex-grow overflow-y-auto overflow-x-hidden relative pb-6">
                <Accordion
                    type="single"
                    collapsible
                    className="w-full space-y-2"
                    value={openAccordion || undefined}
                    onValueChange={setOpenAccordion}
                >
                    {analyses.map((analysis) => (
                        <AccordionItem value={analysis.id} key={analysis.id} className="border-0">
                            <Card className="mx-4 my-2">
                                <AccordionTrigger className="hover:no-underline w-full px-4 py-4">
                                    <div className="flex items-center justify-between w-full">
                                        <div className="flex items-center gap-3">
                                            <RadioTower className="w-4 h-4 text-muted-foreground" />
                                            <div className="text-left">
                                                <p className="text-sm font-medium text-foreground">{analysis.title}</p>
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
                                                        {renderStatus(step)}
                                                        <span className="text-foreground">{step.name}</span>
                                                    </span>
                                                    <span className={
                                                        step.status === 'completed' ? 'text-green-500' : 'text-muted-foreground'
                                                    }>
                                                        {step.status === 'completed' ? step.duration :
                                                            (step.status === 'inProgress' ? 'In Progress' : '-')}
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                        {analysis.agent2Response && (
                                            <div className="mt-4 space-y-3">
                                                <AgentResponseRenderer
                                                    response={analysis.agent1Response}
                                                    title="Agent 1 Response"
                                                    bgColor="bg-red-50 dark:bg-red-900"
                                                />
                                                <AgentResponseRenderer
                                                    response={analysis.agent2Response}
                                                    title="Agent 2 Response"
                                                    bgColor="bg-yellow-50 dark:bg-yellow-900"
                                                />
                                            </div>
                                        )}
                                    </div>
                                </AccordionContent>
                            </Card>
                        </AccordionItem>
                    ))}
                </Accordion>
            </div>
        </div>
    );
}
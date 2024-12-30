// src/utils/artifactTransformer.ts

import { v4 as uuidv4 } from 'uuid';

export interface ChartDataset {
    label: string;
    data: number[];
    color: string;
}

export interface TransformedChartData {
    title: string;
    data: Array<{
        name: string;
        [key: string]: any;
    }>;
    datasets: ChartDataset[];
    style: {
        width: string;
        height: string;
        [key: string]: any;
    };
    options: {
        showGrid: boolean;
        showLegend: boolean;
        axisLabels: {
            x: string;
            y: string;
        };
        interactive: boolean;
    };
}

export interface ArtifactItem {
    id: string;
    component: string;
    sub_type?: string | null;
    data: TransformedChartData | any;
    error?: string;
}

export function transformChartDataForRecharts(rawData: any): TransformedChartData {
    const { labels, values, title, configuration } = rawData;
    
    const data = labels.map((label: string, idx: number) => {
        const dataPoint: any = { name: label };
        values.forEach((item: any) => {
            dataPoint[item.entity] = item.data[idx];
        });
        return dataPoint;
    });

    const datasets = values.map((item: any) => ({
        label: item.entity,
        data: item.data,
        color: `#${Math.floor(Math.random()*16777215).toString(16)}`
    }));

    return {
        title,
        data,
        datasets,
        style: rawData.style || {},
        options: {
            showGrid: configuration?.axes?.showGrid ?? true,
            showLegend: configuration?.legend ?? true,
            axisLabels: {
                x: configuration?.axes?.x?.title || '',
                y: configuration?.axes?.y?.title || ''
            },
            interactive: true
        }
    };
}

export function transformArtifactData(artifact: ArtifactItem): ArtifactItem {
    try {
        const { component, data, sub_type } = artifact;

        switch (component.toLowerCase()) {
            case 'chart': {
                const transformedData = transformChartDataForRecharts(data);
                return {
                    ...artifact,
                    sub_type: sub_type,
                    data: transformedData
                };
            }
            default:
                return artifact;
        }
    } catch (error) {
        console.error("Error transforming artifact data:", error);
        return {
            ...artifact,
            error: error instanceof Error ? error.message : 'Unknown error during transformation'
        };
    }
}

export function processNewArtifact(artifactsData: {
    component: string;
    data: any;
    id?: string;
    sub_type?: string | null;
}): ArtifactItem | null {
    if (!artifactsData) return null;

    const artifact: ArtifactItem = {
        id: artifactsData.id || uuidv4(),
        component: artifactsData.component,
        sub_type: artifactsData.sub_type || null,
        data: artifactsData.data
    };

    return transformArtifactData(artifact);
}

export function isArtifactDuplicate(
    newArtifact: ArtifactItem,
    existingArtifacts: ArtifactItem[]
): boolean {
    return existingArtifacts.some(
        artifact =>
            artifact.component === newArtifact.component &&
            JSON.stringify(artifact.data) === JSON.stringify(newArtifact.data)
    );
}
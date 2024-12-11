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

const getRandomColor = () => `#${Math.floor(Math.random() * 16777215).toString(16)}`;

function transformChartData(rawData: any): TransformedChartData {
    const {
        title = '',
        labels = [],
        values = {},
        style = {},
        axis_labels = { x: '', y: '' },
        config = {}
    } = rawData;

    // Handle both array and object formats for values
    let datasets: ChartDataset[];
    let data: any[];

    if (Array.isArray(values)) {
        // Single dataset case
        datasets = [{
            label: 'Value',
            data: values,
            color: getRandomColor()
        }];

        // Transform into recharts format
        data = labels.map((label: string, index: number) => ({
            name: label,
            Value: values[index]
        }));
    } else {
        // Multiple datasets case
        datasets = Object.entries(values).map(([key, value]) => ({
            label: key,
            data: Array.isArray(value) ? value : [value],
            color: getRandomColor()
        }));

        // Transform into recharts format
        data = labels.map((label: string, index: number) => {
            const dataPoint: { [key: string]: any } = { name: label };
            datasets.forEach(dataset => {
                dataPoint[dataset.label] = dataset.data[index];
            });
            return dataPoint;
        });
    }

    return {
        title,
        data,
        datasets,
        style: {
            width: style.width || '100%',
            height: style.height || '400px',
            ...style
        },
        options: {
            showGrid: config.show_grid ?? true,
            showLegend: config.show_legend ?? true,
            axisLabels: axis_labels,
            interactive: config.interactive ?? true
        }
    };
}

export function transformArtifactData(artifact: ArtifactItem): ArtifactItem {
    try {
        const { component, data, sub_type } = artifact;

        switch (component.toLowerCase()) {
            case 'chart': {
                const transformedData = transformChartData(data);
                return {
                    ...artifact,
                    sub_type: sub_type,
                    data: transformedData
                };
            }
            // Add cases for other component types here
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
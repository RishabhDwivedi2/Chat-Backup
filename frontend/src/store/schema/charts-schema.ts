// src/store/schema/charts-schema.ts

interface BaseChartData {
    title?: string;
    labels: string[];
    datasets: {
        label: string;
        data: number[];
        color?: string;
    }[];
    style?: {
        chartBackgroundColor?: string;
        chartBorderColor?: string;
        barThickness?: number;
        strokeWidth?: number;
        fillOpacity?: number;
    };
    options?: Record<string, any>;
}

export interface BarChartData extends BaseChartData {
    chartType: 'Bar';
    options?: {
        barSize?: number;
        stackId?: string;
        maxBarSize?: number;
        minBarSize?: number;
        [key: string]: any;
    };
}

export interface LineChartData extends BaseChartData {
    chartType: 'Line';
    options?: {
        type?: 'monotone' | 'linear' | 'step';
        activeDot?: boolean | object;
        dot?: boolean | object;
        connectNulls?: boolean;
        [key: string]: any;
    };
}

export interface PieChartData extends BaseChartData {
    chartType: 'Pie';
    options?: {
        innerRadius?: number | string;
        outerRadius?: number | string;
        paddingAngle?: number;
        startAngle?: number;
        endAngle?: number;
        [key: string]: any;
    };
}

export interface AreaChartData extends BaseChartData {
    chartType: 'Area';
    options?: {
        type?: 'monotone' | 'linear' | 'step';
        stackId?: string;
        connectNulls?: boolean;
        [key: string]: any;
    };
}

export interface RadarChartData extends BaseChartData {
    chartType: 'Radar';
    options?: {
        polarAngleAxis?: object;
        polarGridType?: 'polygon' | 'circle';
        gridType?: string;
        [key: string]: any;
    };
}

export interface RadialChartData extends BaseChartData {
    chartType: 'Radial';
    options?: {
        startAngle?: number;
        endAngle?: number;
        minAngle?: number;
        background?: boolean;
        clockWise?: boolean;
        [key: string]: any;
    };
}

export type ChartData = 
    | BarChartData 
    | LineChartData 
    | PieChartData 
    | AreaChartData 
    | RadarChartData 
    | RadialChartData;

export interface ChartDataset {
    label: string;
    data: number[];
    color?: string;
}
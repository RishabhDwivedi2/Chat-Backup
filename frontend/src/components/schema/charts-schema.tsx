import { CSSProperties } from 'react';

interface BaseChartData {
    title?: string;
    labels: string[];
    style?: {
        chartBackgroundColor?: string;
        chartBorderColor?: string;
    } & CSSProperties;
}

interface Dataset {
    label: string;
    data: number[];
    color?: string;
}

interface BarChartData extends BaseChartData {
    chartType: 'Bar';
    datasets: Dataset[];
    style?: BaseChartData['style'] & {
        barThickness?: number;
    };
}

interface LineChartData extends BaseChartData {
    chartType: 'Line';
    datasets: Dataset[];
    style?: BaseChartData['style'] & {
        strokeWidth?: number;
    };
}

interface PieChartData extends BaseChartData {
    chartType: 'Pie';
    datasets: [Dataset]; 
}

interface AreaChartData extends BaseChartData {
    chartType: 'Area';
    datasets: Dataset[];
    style?: BaseChartData['style'] & {
        fillOpacity?: number;
    };
}

interface RadarChartData extends BaseChartData {
    chartType: 'Radar';
    datasets: Dataset[];
    style?: BaseChartData['style'] & {
        fillOpacity?: number;
    };
}

interface RadialChartData extends BaseChartData {
    chartType: 'Radial';
    datasets: [Dataset]; 
    style?: BaseChartData['style'] & {
        barThickness?: number;
    };
}

type ChartData = BarChartData | LineChartData | PieChartData | AreaChartData | RadarChartData | RadialChartData;

export type { ChartData, BarChartData, LineChartData, PieChartData, AreaChartData, RadarChartData, RadialChartData };
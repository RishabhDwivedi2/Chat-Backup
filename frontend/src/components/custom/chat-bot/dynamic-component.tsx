// src/components/custom/chat-bot/dynamic-component.tsx

import React, { useRef, useEffect, useMemo, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import {
    BarChart, Bar, LineChart, Line, PieChart, Pie,
    AreaChart, Area, RadarChart, Radar, PolarGrid,
    PolarAngleAxis, RadialBarChart, RadialBar, PolarRadiusAxis,
    ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Cell,
    ScatterChart
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { transformChartDataForRecharts, TransformedChartData } from '@/utils/artifactTransformer';

interface BaseComponentData {
    title?: string;
    style?: React.CSSProperties;
}

interface TableData extends BaseComponentData {
    headers: string[];
    rows: Record<string, any>[];
    style?: {
        headerColor?: string;
        cellColor?: string;
        headerFontSize?: string;
        cellFontSize?: string;
    } & React.CSSProperties;
}

interface CardData extends BaseComponentData {
    labels?: string[];
    values?: string[];
    metrics?: Array<Record<string, any>>;
    footer?: string;
    content?: string | Record<string, string | string[]>;
}

interface TextData extends BaseComponentData {
    text: string;
    style?: {
        textColor?: string;
        fontSize?: string;
        fontStyle?: string;
    };
}

type ComponentData = TableData | TransformedChartData | CardData | TextData;

interface DynamicComponentProps {
    component: string;
    data: ComponentData;
    sub_type?: string;
}

const CHART_COLORS = [
    '#FF6B6B', // Red
    '#4ECDC4', // Teal
    '#45B7D1', // Blue
    '#96CEB4', // Green
    '#FFEEAD', // Yellow
    '#D4A5A5', // Pink
    '#9370DB', // Purple
    '#20B2AA', // Light Sea Green
    '#FF8C42', // Orange
    '#98D8D8'  // Light Blue
];

const DynamicComponent: React.FC<DynamicComponentProps> = React.memo(({ component, data, sub_type }) => {
    console.log("Dynamic C. Component:", component, "Sub_type:", sub_type, "Data:", data);

    const uniqueId = useRef(uuidv4());
    const chartColorsRef = useRef<string[]>([]);

    const getChartColor = useCallback((index: number) => {
        return CHART_COLORS[index % CHART_COLORS.length];
    }, []);

    const validateTableData = useCallback((data: any): data is TableData =>
        Array.isArray(data.headers) && Array.isArray(data.rows), []);

    const validateChartData = useCallback((data: any): data is TransformedChartData => {
        if (data.labels && data.values) {
            const transformedData = transformChartDataForRecharts(data);
            Object.assign(data, transformedData);
        }
        
        return data && Array.isArray(data.data) && Array.isArray(data.datasets);
    }, []);
    
    const validateTextData = useCallback((data: any): data is TextData =>
        typeof data.text === 'string', []);

    const styleTagContent = useMemo(() => {
        if ('headers' in data && data.style) {
            const { headerColor, headerFontSize, cellColor, cellFontSize } = data.style;
            return `
                .component-${uniqueId.current} .table-header { 
                    color: ${headerColor || 'inherit'}; 
                    font-size: ${headerFontSize || 'inherit'}; 
                }
                .component-${uniqueId.current} .table-cell { 
                    color: ${cellColor || 'inherit'}; 
                    font-size: ${cellFontSize || 'inherit'}; 
                }
            `;
        }
        return '';
    }, [data]);

    useEffect(() => {
        if (!styleTagContent) return;

        const styleTag = document.createElement('style');
        styleTag.innerHTML = styleTagContent;
        document.head.appendChild(styleTag);
        return () => {
            document.head.removeChild(styleTag);
        };
    }, [styleTagContent]);

    const renderTable = useCallback(() => {
        if (!validateTableData(data)) {
            return <p>Error: Invalid table data</p>;
        }
    
        const transformedRows = Array.isArray(data.rows[0]) 
            ? data.rows 
            : data.rows.map(rowObj => 
                data.headers.map(header => rowObj[header] || '')
            );
    
        return (
            <Card className="w-full h-full flex flex-col">
                {data.title && (
                    <CardHeader>
                        <CardTitle>{data.title}</CardTitle>
                    </CardHeader>
                )}
                <CardContent className="flex-1 min-h-0 p-0">
                    <div className="w-full h-full relative">
                        <div className="absolute inset-0 overflow-auto">
                            <div className="min-w-full w-fit">
                                <Table>
                                    <TableHeader className="sticky top-0 bg-background z-10">
                                        <TableRow>
                                            {data.headers.map((header, index) => (
                                                <TableHead 
                                                    key={index} 
                                                    className="table-header whitespace-nowrap bg-muted"
                                                >
                                                    {header}
                                                </TableHead>
                                            ))}
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {transformedRows.map((row, rowIndex) => (
                                            <TableRow key={rowIndex}>
                                                {row.map((cell: any, cellIndex: number) => (
                                                    <TableCell
                                                        key={cellIndex}
                                                        className="table-cell whitespace-nowrap"
                                                    >
                                                        {typeof cell === 'object' 
                                                            ? JSON.stringify(cell) 
                                                            : String(cell)
                                                        }
                                                    </TableCell>
                                                ))}
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>
        );
    }, [data, validateTableData]);

    const renderBarChart = useCallback((chartData: TransformedChartData) => (
        <BarChart 
            data={chartData.data} 
            margin={{ 
                top: 20, 
                right: 30, 
                left: 50,  
                bottom: 30  
            }}
        >
            <CartesianGrid 
                strokeDasharray="3 3" 
                opacity={0.2} 
            />
            <XAxis 
                dataKey="name"
                label={{ 
                    value: chartData.options.axisLabels.x,
                    position: 'bottom',
                    offset: -20
                }}
                tick={{ fontSize: 12 }}
            />
            <YAxis
                label={{ 
                    value: chartData.options.axisLabels.y,
                    angle: -90,
                    position: 'insideLeft',
                    offset: -35
                }}
                tick={{ fontSize: 12 }}
                domain={['auto', 'auto']}
            />
            <Tooltip />
            {chartData.options.showLegend && <Legend />}
            {chartData.datasets.map((dataset) => (
                <Bar 
                    key={dataset.label}
                    dataKey={dataset.label}
                    name={dataset.label}
                    fill={dataset.color}
                />
            ))}
        </BarChart>
    ), []);

    const renderLineChart = useCallback((chartData: TransformedChartData) => (
        <LineChart data={chartData.data}>
            {chartData.options.showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey="name" />
            <YAxis
                width={60}
                tickFormatter={(value) => typeof value === 'number' ? value.toLocaleString() : value}
            />
            <Tooltip />
            {chartData.options.showLegend && <Legend />}
            {chartData.datasets.map((dataset, index) => (
                <Line
                    key={dataset.label}
                    type="monotone"
                    dataKey={dataset.label}
                    stroke={dataset.color || getChartColor(index)}
                />
            ))}
        </LineChart>
    ), [getChartColor]);

    const renderAreaChart = useCallback((chartData: TransformedChartData) => (
        <AreaChart data={chartData.data}>
            {chartData.options.showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey="name" />
            <YAxis
                width={60}
                tickFormatter={(value) => typeof value === 'number' ? value.toLocaleString() : value}
            />
            <Tooltip />
            {chartData.options.showLegend && <Legend />}
            {chartData.datasets.map((dataset, index) => (
                <Area
                    key={dataset.label}
                    type="monotone"
                    dataKey={dataset.label}
                    fill={dataset.color || getChartColor(index)}
                    stroke={dataset.color || getChartColor(index)}
                    fillOpacity={0.3}
                />
            ))}
        </AreaChart>
    ), [getChartColor]);

    const renderPieChart = useCallback((chartData: TransformedChartData) => (
        <PieChart>
            <Pie
                data={chartData.data}
                dataKey={chartData.datasets[0].label}
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={80}
                label
            >
                {chartData.data.map((entry, index) => (
                    <Cell
                        key={`cell-${index}`}
                        fill={chartData.datasets[0].color || getChartColor(index)}
                    />
                ))}
            </Pie>
            <Tooltip />
            {chartData.options.showLegend && <Legend />}
        </PieChart>
    ), [getChartColor]);

    const renderRadarChart = useCallback((chartData: TransformedChartData) => (
        <RadarChart data={chartData.data} cx="50%" cy="50%" outerRadius="80%">
            <PolarGrid />
            <PolarAngleAxis dataKey="name" />
            <PolarRadiusAxis angle={90} domain={[0, 100]} />
            {chartData.datasets.map((dataset, index) => (
                <Radar
                    key={dataset.label}
                    name={dataset.label}
                    dataKey={dataset.label === 'Value' ? 'Value' : dataset.label}
                    fill={dataset.color || getChartColor(index)}
                    fillOpacity={0.6}
                    stroke={dataset.color || getChartColor(index)}
                />
            ))}
            <Tooltip />
            {chartData.options.showLegend && <Legend />}
        </RadarChart>
    ), [getChartColor]);

    const renderRadialBarChart = useCallback((chartData: TransformedChartData) => (
        <RadialBarChart
            innerRadius="10%"
            outerRadius="80%"
            data={chartData.data}
            startAngle={180}
            endAngle={0}
            cx="50%"
            cy="50%"
        >
            <RadialBar
                label={{
                    position: 'insideStart',
                    fill: '#666'
                }}
                background
                dataKey={chartData.datasets[0].label === 'Value' ? 'Value' : chartData.datasets[0].label}
            >
                {chartData.data.map((entry, index) => (
                    <Cell
                        key={`cell-${index}`}
                        fill={chartData.datasets[0].color || getChartColor(index)}
                    />
                ))}
            </RadialBar>
            <Tooltip />
            {chartData.options.showLegend && <Legend
                iconSize={10}
                layout="vertical"
                verticalAlign="middle"
                align="right"
                wrapperStyle={{ lineHeight: '40px' }}
            />}
        </RadialBarChart>
    ), [getChartColor]);

    const renderChart = useCallback(() => {
        if (!validateChartData(data)) return <p>Error: Invalid chart data</p>;

        const chartData = data as TransformedChartData;
        const chartHeight = parseInt(chartData.style.height as string) || 400;
        const chartType = sub_type?.toLowerCase();

        const getChartComponent = () => {
            switch (chartType) {
                case 'bar':
                    return renderBarChart(chartData);
                case 'line':
                    return renderLineChart(chartData);
                case 'area':
                    return renderAreaChart(chartData);
                case 'pie':
                    return renderPieChart(chartData);
                case 'radar':
                    return renderRadarChart(chartData);
                case 'radial':
                    return renderRadialBarChart(chartData);
                default:
                    return <div>Unsupported chart type: {chartType}</div>;
            }
        };

        return (
            <Card className="w-full h-full flex flex-col">
                {chartData.title && (
                    <CardHeader>
                        <CardTitle>{chartData.title}</CardTitle>
                    </CardHeader>
                )}
                <CardContent className="flex-1 min-h-0 p-4">
                    <div className="w-full" style={{ height: `${chartHeight}px`, minHeight: '400px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            {getChartComponent()}
                        </ResponsiveContainer>
                    </div>
                </CardContent>
            </Card>
        );
    }, [data, sub_type, validateChartData, renderBarChart, renderLineChart, renderAreaChart]);


    const renderCard = useCallback(() => {
        const cardData = data as CardData;

        const validateCardData = (data: any): data is CardData => {
            return (
                (('labels' in data && 'values' in data) || 'content' in data) &&
                'title' in data
            );
        };

        if (!validateCardData(cardData)) {
            return <p>Error: Invalid card data</p>;
        }

        return (
            <Card
                className="w-full relative"
                style={{
                    maxWidth: cardData.style?.width || '100%',
                    maxHeight: cardData.style?.height || 'none',
                    height: 'auto',
                    overflow: 'auto' 
                }}
            >
                {cardData.title && (
                    <CardHeader className="sticky top-0 bg-card z-10">
                        <CardTitle>{cardData.title}</CardTitle>
                    </CardHeader>
                )}
                <CardContent className="overflow-y-auto">
                    {cardData.content && (
                        typeof cardData.content === 'string' ? (
                            <p>{cardData.content}</p>
                        ) : (
                            Object.entries(cardData.content).map(([key, value]) => (
                                <div key={key} className="mb-2">
                                    <strong>{key}:</strong>{' '}
                                    <span>{Array.isArray(value) ? value.join(', ') : value}</span>
                                </div>
                            ))
                        )
                    )}

                    {cardData.labels && cardData.values && (
                        <div className="space-y-6">
                            {cardData.labels.map((label, index) => (
                                <div key={index} className="flex flex-col border-b last:border-0 pb-4 last:pb-0">
                                    <div className="text-sm font-medium text-muted-foreground">
                                        {label}
                                    </div>
                                    <div className="text-lg font-semibold mt-1">
                                        {cardData.values?.[index]}
                                    </div>
                                    {cardData.metrics?.[index] && (
                                        <div className="mt-3 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 text-sm">
                                            {Object.entries(cardData.metrics[index]).map(([key, value]) => (
                                                <div key={key} className="flex flex-col p-2 bg-muted/50 rounded-lg">
                                                    <span className="text-muted-foreground text-xs">{key}</span>
                                                    <span className="font-medium mt-1">
                                                        {typeof value === 'number'
                                                            ? value.toLocaleString()
                                                            : value}
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>

                {cardData.footer && (
                    <div className="p-6 pt-0 sticky bottom-0 bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/75">
                        <p className="text-sm text-muted-foreground">
                            {cardData.footer}
                        </p>
                    </div>
                )}
            </Card>
        );
    }, [data]);

    const renderText = useCallback(() => {
        if (!validateTextData(data)) {
            return <p>Error: Invalid text data</p>;
        }

        const textData = data as TextData;
        return (
            <div className={`component-${uniqueId.current} text-component`}>
                {textData.title && <h3 className="text-lg font-semibold mb-2">{textData.title}</h3>}
                <p style={textData.style}>{textData.text}</p>
            </div>
        );
    }, [data, validateTextData]);

    const renderComponent = useMemo(() => {
        try {
            const normalizedComponent = component.toLowerCase();
            switch (normalizedComponent) {
                case 'table':
                    return renderTable();
                case 'chart':
                    return renderChart();
                case 'card':
                    return renderCard();
                case 'text':
                    return renderText();
                default:
                    return <p>Unknown component type: {component}</p>;
            }
        } catch (error) {
            console.error("Error in DynamicComponent:", error);
            return (
                <div className="p-4 border border-red-200 rounded-md bg-red-50">
                    <p className="text-red-500">Error rendering component</p>
                    {error instanceof Error && (
                        <p className="text-sm text-red-400 mt-1">{error.message}</p>
                    )}
                </div>
            );
        }
    }, [component, renderTable, renderChart, renderCard, renderText]);

    return renderComponent;
});

DynamicComponent.displayName = 'DynamicComponent';

export default DynamicComponent;
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
import { TransformedChartData } from '@/utils/artifactTransformer';
import YAxisWrapper from '@/utils/YAxisWrapper';
import XAxisWrapper from '@/utils/XAxisWrapper';

// Move interfaces outside component
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
    content?: string | Record<string, string | string[]>; // Keep for backward compatibility
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

const DynamicComponent: React.FC<DynamicComponentProps> = React.memo(({ component, data, sub_type }) => {
    console.log("Dynamic C. Component:", component, "Sub_type:", sub_type, "Data:", data);
    
    const uniqueId = useRef(uuidv4());
    const chartColorsRef = useRef<string[]>([]);

    // Initialize chart colors
    useEffect(() => {
        if (chartColorsRef.current.length === 0) {
            chartColorsRef.current = Array(10).fill(null).map(() => 
                `#${Math.floor(Math.random() * 16777215).toString(16)}`
            );
        }
    }, []);

    const getChartColor = useCallback((index: number) => {
        return chartColorsRef.current[index % chartColorsRef.current.length];
    }, []);

    // Validation functions
    const validateTableData = useCallback((data: any): data is TableData => 
        Array.isArray(data.headers) && Array.isArray(data.rows), []);

    const validateChartData = useCallback((data: any): data is TransformedChartData => 
        'datasets' in data && Array.isArray(data.datasets) && 'data' in data, []);

    const validateTextData = useCallback((data: any): data is TextData => 
        typeof data.text === 'string', []);

    // Style handling
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
        
        // Transform object rows into arrays based on headers
        const transformedRows = (data.rows as Record<string, any>[]).map(rowObj => 
            data.headers.map(header => rowObj[header] || '')
        );
        
        return (
            <Card className="w-full">
                {data.title && (
                    <CardHeader>
                        <CardTitle>{data.title}</CardTitle>
                    </CardHeader>
                )}
                <CardContent>
                    <div className="relative w-full overflow-auto" 
                         style={{ 
                             maxHeight: data.style?.height || '500px',
                             maxWidth: data.style?.width || '100%'
                         }}>
                        <Table>
                            <TableHeader className="sticky top-0 bg-background z-10">
                                <TableRow>
                                    {data.headers.map((header, index) => (
                                        <TableHead key={index} className="table-header whitespace-nowrap">
                                            {header}
                                        </TableHead>
                                    ))}
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {transformedRows.map((row, rowIndex) => (
                                    <TableRow key={rowIndex}>
                                        {row.map((cell, cellIndex) => (
                                            <TableCell 
                                                key={cellIndex} 
                                                className="table-cell"
                                            >
                                                {typeof cell === 'object' ? JSON.stringify(cell) : cell}
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </div>
                </CardContent>
            </Card>
        );
    }, [data, validateTableData]);

    const renderBarChart = useCallback((chartData: TransformedChartData) => (
        <BarChart data={chartData.data}>
            {chartData.options.showGrid && <CartesianGrid strokeDasharray="3 3" />}
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            {chartData.options.showLegend && <Legend />}
            {chartData.datasets.map((dataset, index) => (
                <Bar key={dataset.label} dataKey={dataset.label} fill={dataset.color || getChartColor(index)} />
            ))}
        </BarChart>
    ), [getChartColor]);    

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
                    // Removed data prop as it's not needed - RadarChart handles the data
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
                // Removed minAngle as it's not in the type definition
                label={{ 
                    position: 'insideStart',
                    fill: '#666'
                    // Removed formatter as it's causing type issues
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
            <Card className="w-full">
                {chartData.title && (
                    <CardHeader>
                        <CardTitle>{chartData.title}</CardTitle>
                    </CardHeader>
                )}
                <CardContent>
                    <div style={{ width: '100%', height: `${chartHeight}px` }}>
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
        
        // Validate the card data structure
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
                    height: 'auto', // Allow content to determine height
                    overflow: 'auto' // Add scroll if content exceeds maxHeight
                }}
            >
                {cardData.title && (
                    <CardHeader className="sticky top-0 bg-card z-10">
                        <CardTitle>{cardData.title}</CardTitle>
                    </CardHeader>
                )}
                <CardContent className="overflow-y-auto">
                    {/* Handle legacy content format */}
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
                    
                    {/* Handle new data format */}
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

    // Main render logic
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
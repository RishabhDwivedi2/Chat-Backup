'use client'
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

type DataItem = {
  name: string;
  value: number | string;
};

function ensureDataFormat(data: any): DataItem[] {
  if (data && data.table && data.table.columns && data.table.rows) {
    // Handle the specific structure provided in the error message
    return data.table.rows.map((row: any, index: number) => ({
      name: row[0],
      value: row[1] // You might want to parse this to a number if possible
    }));
  } else if (Array.isArray(data)) {
    return data.map(item => ({
      name: String(item.name || item.category || ''),
      value: item.value
    }));
} else if (typeof data === 'object' && data !== null) {
    return Object.entries(data).map(([key, value]) => ({

      name: String(key),

      value: typeof value === 'number' || typeof value === 'string' ? value : String(value) // Ensure value is string or number

    }));

  }
  return [];
}

export function ArtifactPanel({ component, data }: { component: string; data: any }) {
  const formattedData = ensureDataFormat(data);

  console.log("Raw Data:", data);  // Add this line for debugging
  console.log("Formatted Data:", formattedData);  // Add this line for debugging

  const renderComponent = () => {
    switch (component) {
      case 'BarChart':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={formattedData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        );
      case 'LineChart':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={formattedData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="value" stroke="#8884d8" />
            </LineChart>
          </ResponsiveContainer>
        );
      case 'PieChart':
        return (
          <ResponsiveContainer width="100%" height={400}>
            <PieChart>
              <Pie
                data={formattedData}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {formattedData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        );
      case 'Table':
        return (
          <div className="overflow-x-auto">
            <table className="min-w-full bg-white">
              <thead>
                <tr>
                  <th className="px-4 py-2 bg-gray-100">Name</th>
                  <th className="px-4 py-2 bg-gray-100">Value</th>
                </tr>
              </thead>
              <tbody>
                {formattedData.map((item, index) => (
                  <tr key={index} className={index % 2 === 0 ? 'bg-gray-50' : ''}>
                    <td className="px-4 py-2">{item.name}</td>
                    <td className="px-4 py-2">{item.value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      default:
        return <div>Unsupported component type</div>;
    }
  };

  return (
    <div className="p-4 border rounded shadow mt-4">
      <h2 className="text-lg font-bold mb-2">Artifact Panel</h2>
      {formattedData.length > 0 ? renderComponent() : <div>No data to display</div>}
    </div>
  );
}
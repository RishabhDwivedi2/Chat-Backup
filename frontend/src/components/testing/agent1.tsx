'use client'
import { useState } from 'react';

const UI_COMPONENTS = ['BarChart', 'LineChart', 'Table', 'PieChart'];

export function ResponderAgent1({ query, onSelectComponent }: { query: string; onSelectComponent: (component: string) => void }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectUIComponent = async () => {
    setLoading(true);
    setError(null);

    if (!query.trim()) {
      setError("Please enter a query before selecting a UI component.");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('/api/openai1', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query.trim() }),
      });

      const data = await response.json();

      console.log("Agent 1 Response:", data);


      if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.status} ${response.statusText}. Error: ${JSON.stringify(data)}`);
      }

      if (data.component && UI_COMPONENTS.includes(data.component)) {
        onSelectComponent(data.component);
      } else {
        setError(`Invalid component selected: ${data.component || 'Unknown'}`);
      }
    } catch (error: any) {
      console.error("Error selecting UI component:", error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 border rounded shadow">
      <h2 className="text-lg font-bold mb-2">Responder Agent 1 (UI Selection)</h2>
      <button
        onClick={selectUIComponent}
        disabled={loading || !query.trim()}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
      >
        {loading ? 'Selecting...' : 'Select UI Component'}
      </button>
      {error && <p className="text-red-500 mt-2">{error}</p>}
    </div>
  );
}
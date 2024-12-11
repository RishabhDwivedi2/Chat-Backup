// src/components/testing/agent2.tsx
'use client'
import { useState } from 'react';

export function ResponderAgent2({ query, selectedComponent, onDataRetrieved }: { query: string; selectedComponent: string; onDataRetrieved: (data: any) => void }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const retrieveData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/openai2', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query, selectedComponent }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.status} ${response.statusText}. Error: ${JSON.stringify(data)}`);
      }

      onDataRetrieved(data);
    } catch (error : any) {
      console.error("Error retrieving data:", error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 border rounded shadow mt-4">
      <h2 className="text-lg font-bold mb-2">Responder Agent 2 (Data Retrieval)</h2>
      <button
        onClick={retrieveData}
        disabled={loading || !selectedComponent}
        className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:bg-gray-400"
      >
        {loading ? 'Retrieving...' : 'Retrieve Data'}
      </button>
      {error && <p className="text-red-500 mt-2">{error}</p>}
    </div>
  );
}
'use client'
import React, { useEffect, useState, useCallback } from 'react';

const Chat: React.FC = () => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [messages, setMessages] = useState<string[]>([]);
  const [input, setInput] = useState<string>('');
  const [connectionStatus, setConnectionStatus] = useState<string>('Connecting...');

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:3002');
    
    ws.onopen = () => {
      console.log('Connected to WebSocket');
      setConnectionStatus('Connected');
      setSocket(ws);
    };

    ws.onmessage = (event: MessageEvent) => {
      console.log('Received message:', event.data);
      setMessages((prev) => [...prev, event.data]);
    };

    ws.onclose = (event) => {
      console.log('WebSocket closed:', event);
      setConnectionStatus('Disconnected');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnectionStatus('Error: ' + error.toString());
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  const sendMessage = useCallback(() => {
    if (socket && socket.readyState === WebSocket.OPEN && input.trim()) {
      socket.send(input);
      setInput('');
    } else {
      console.error('Cannot send message. WebSocket is not open.');
    }
  }, [socket, input]);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Chat</h1>
      <p>Status: {connectionStatus}</p>
      <div className="mb-4 h-64 overflow-y-auto border p-2">
        {messages.map((msg, idx) => (
          <div key={idx} className="mb-2">{msg}</div>
        ))}
      </div>
      <div className="flex">
        <input
          type="text"
          value={input}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
          placeholder="Type a message"
          className="flex-grow border p-2 mr-2"
        />
        <button onClick={sendMessage} className="bg-blue-500 text-white px-4 py-2 rounded">Send</button>
      </div>
    </div>
  );
};

export default Chat;
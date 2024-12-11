//File: src/utils/socket.ts

import WebSocket, { WebSocketServer } from 'ws';

let wss: WebSocketServer | undefined;

export const startWebSocketServer = () => {
  wss = new WebSocketServer({ port: 8081 });

  wss.on('connection', (ws: WebSocket) => {
    console.log('Client connected to Chat');

    ws.on('close', () => {
      console.log('Client disconnected from Chat');
    });

    ws.send(JSON.stringify({ status: 'Chat is running' }));

    // Ensure graceful shutdown
    process.on('exit', () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ status: 'Chat is shutting down' }));
      }
    });
  });

  console.log('WebSocket server running on ws://localhost:8081');
};

// Call this function in your Next.js custom server or API route
// startWebSocketServer();

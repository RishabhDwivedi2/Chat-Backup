import express from 'express';
import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import cors from 'cors';

const app = express();
app.use(cors());

const server = createServer(app);
const wss = new WebSocketServer({ server });

wss.on('connection', (ws, req) => {
  console.log('A user connected from:', req.socket.remoteAddress);
  
  ws.on('message', (message) => {
    console.log('Message received:', message.toString());
    // Broadcast the message to all clients
    wss.clients.forEach((client) => {
      if (client.readyState === WebSocketServer.OPEN) {
        client.send(message.toString());
      }
    });
  });

  ws.on('close', () => {
    console.log('User disconnected');
  });

  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
  });
});

server.listen(3002, () => {
  console.log('WebSocket server listening on port 3002');
});

// Handle server errors
server.on('error', (error) => {
  console.error('Server error:', error);
});
import { NextRequest, NextResponse } from 'next/server';
import WebSocket from 'ws';

const openAIWebSocketURL = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01";

export async function GET(req: NextRequest) {
  const wss = new WebSocket.Server({ noServer: true });

  wss.on('connection', (ws) => {
    console.log('New WebSocket connection');

    const openAIWs = new WebSocket(openAIWebSocketURL, {
      headers: {
        "Authorization": `Bearer ${process.env.OPENAI_API_KEY}`,
        "OpenAI-Beta": "realtime=v1"
      }
    });

    openAIWs.on('open', () => {
      console.log('Connected to OpenAI WebSocket');
      openAIWs.send(JSON.stringify({
        type: "response.create",
        response: {
          modalities: ["speech"],
          instructions: "Convert the incoming speech to text, then generate a spoken response.",
        }
      }));
    });

    openAIWs.on('message', (message) => {
      const data = JSON.parse(message.toString());
      if (data.type === 'response.chunk' && data.chunk.speech) {
        ws.send(JSON.stringify({
          type: 'audio',
          audio: data.chunk.speech
        }));
      }
    });

    openAIWs.on('error', (error) => {
      console.error('OpenAI WebSocket error:', error);
      ws.close(1011, 'OpenAI WebSocket error');
    });

    ws.on('message', (message) => {
      if (openAIWs.readyState === WebSocket.OPEN) {
        openAIWs.send(JSON.stringify({
          type: 'request.chunk',
          chunk: {
            speech: message
          }
        }));
      }
    });

    ws.on('close', (code, reason) => {
      console.log(`Client WebSocket connection closed: ${code} ${reason}`);
      openAIWs.close();
    });

    ws.on('error', (error) => {
      console.error('Client WebSocket error:', error);
    });

    openAIWs.on('close', (code, reason) => {
      console.log(`OpenAI WebSocket connection closed: ${code} ${reason}`);
      ws.close(1011, 'OpenAI WebSocket closed');
    });
  });

  return new NextResponse('WebSocket server is running', { status: 200 });
}

export const config = {
  api: {
    bodyParser: false,
  },
};
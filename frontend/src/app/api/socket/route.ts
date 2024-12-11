// import { NextResponse } from 'next/server';
// import { Server as SocketIOServer } from 'socket.io';
// import type { Server as HTTPServer } from 'http';
// import type { Socket as NetSocket } from 'net';

// interface SocketServer extends HTTPServer {
//   io?: SocketIOServer;
// }

// interface SocketWithIO extends NetSocket {
//   server: SocketServer;
// }

// export const dynamic = 'force-dynamic';

// let io: SocketIOServer;

// export async function GET(req: Request) {
//   if (io) {
//     // If Socket.IO server is already running, we can skip initialization
//     return NextResponse.json({ message: 'Socket is already running' });
//   }

//   try {
//     const res = NextResponse.next() as NextResponse<{ socket: { server: SocketServer } }>;
//     const httpServer = (res as any).socket?.server as SocketServer; // Use 'any' to bypass type checking


//     if (!httpServer.io) {
//       console.log('Initializing Socket.IO server...');
//       io = new SocketIOServer(httpServer, {
//         path: '/api/socket',
//         addTrailingSlash: false,
//       });

//       httpServer.io = io;

//       io.on('connection', (socket) => {
//         console.log(`Socket ${socket.id} connected`);

//         socket.on('toggleMic', (data: { isMuted: boolean }) => {
//           console.log('Mic toggled:', data);
//           // Handle mic toggle event
//         });

//         socket.on('disconnect', () => {
//           console.log(`Socket ${socket.id} disconnected`);
//         });
//       });
//     } else {
//       console.log('Socket.IO server already running');
//       io = httpServer.io;
//     }

//     return NextResponse.json({ message: 'Socket initialized' });
//   } catch (error) {
//     console.error('Error initializing Socket.IO:', error);
//     return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
//   }
// }
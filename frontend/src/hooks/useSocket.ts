// File: src/hooks/useSocket.ts
import { useEffect, useState } from 'react'
import io, { Socket } from 'socket.io-client'

export const useSocket = () => {
  const [socket, setSocket] = useState<Socket | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const socketInitializer = async () => {
      await fetch('/api/socketio')
      const newSocket = io({
        path: '/api/socketio',
      })

      newSocket.on('connect', () => {
        console.log('Connected to WebSocket')
        setError(null)
      })

      newSocket.on('connect_error', (err) => {
        console.error('Socket connection error:', err)
        setError('Failed to connect to the server. Please try again later.')
      })

      setSocket(newSocket)
    }

    socketInitializer()

    return () => {
      if (socket) {
        socket.disconnect()
      }
    }
  }, [])

  return { socket, error }
}

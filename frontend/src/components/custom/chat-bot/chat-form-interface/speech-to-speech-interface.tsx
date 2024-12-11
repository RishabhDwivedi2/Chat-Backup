import React, { useState, useEffect, useRef } from 'react';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { Button } from "@/components/ui/button";
import { Mic, MicOff } from "lucide-react";
import RippleEffect from "@/components/magicui/ripple";

interface SpeechProps {
  isOpen: boolean;
  onClose: () => void;
}

const Speech: React.FC<SpeechProps> = ({ isOpen, onClose }) => {
  const [isListening, setIsListening] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const apiStartTimeRef = useRef<number>(0);

  useEffect(() => {
    if (isOpen) {
      socketRef.current = new WebSocket('ws://localhost:3002/api/speech-to-speech');

      socketRef.current.onopen = () => {
        console.log('Connected to WebSocket');
      };

      socketRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'audio') {
          const endTime = performance.now();
          const duration = endTime - apiStartTimeRef.current;
          console.log(`API response time: ${duration.toFixed(2)}ms`);
          
          playAudio(data.audio);
        }
      };

      socketRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      socketRef.current.onclose = () => {
        console.log('WebSocket connection closed');
      };

      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
    }

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [isOpen]);

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const startListening = () => {
    setIsListening(true);
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        mediaRecorderRef.current = new MediaRecorder(stream);
        let audioChunks: Blob[] = [];

        mediaRecorderRef.current.ondataavailable = (event) => {
          audioChunks.push(event.data);
        };

        mediaRecorderRef.current.onstop = () => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
          sendAudioToServer(audioBlob);
          audioChunks = [];
        };

        mediaRecorderRef.current.start();

        const silenceDetectionInterval = setInterval(() => {
          if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
            mediaRecorderRef.current.stop();
            mediaRecorderRef.current.start();
          }
        }, 3000); // Check for silence every 3 seconds

        return () => {
          clearInterval(silenceDetectionInterval);
          if (mediaRecorderRef.current) {
            mediaRecorderRef.current.stop();
          }
        };
      })
      .catch(error => console.error('Error accessing microphone:', error));
  };

  const stopListening = () => {
    setIsListening(false);
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
  };

  const sendAudioToServer = (audioBlob: Blob) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      apiStartTimeRef.current = performance.now();
      socketRef.current.send(audioBlob);
    }
  };

  const playAudio = (audioData: ArrayBuffer) => {
    if (audioContextRef.current) {
      audioContextRef.current.decodeAudioData(audioData, (buffer) => {
        const source = audioContextRef.current!.createBufferSource();
        source.buffer = buffer;
        source.connect(audioContextRef.current!.destination);
        source.start(0);
      });
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-none max-h-none w-screen h-screen" style={{ borderRadius: '0' }}>
        <div className="relative flex w-full h-full items-center justify-center overflow-hidden">
          <RippleEffect />
          <Button 
            variant="ghost" 
            size="icon" 
            className={`
              absolute z-20 rounded-full w-20 h-20
              bg-primary hover:bg-primary/90
              text-primary-foreground hover:text-primary-foreground
              transition-colors duration-200
            `}
            onClick={toggleListening}
          >
            {isListening ? (
              <MicOff className="w-10 h-10" />
            ) : (
              <Mic className="w-10 h-10" />
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default Speech;
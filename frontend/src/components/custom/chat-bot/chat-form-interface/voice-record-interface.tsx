// File: src/components/custom/chat-bot/chat-form-interface/voice-record-interface.tsx

import React, { useState, useEffect, useRef } from 'react';
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { X, Check } from "lucide-react";
import { SpokeSpinner } from "../../../ui/spinner";

interface VoiceRecordingInterfaceProps {
  onCancel: () => void;
  onSave: (transcribedText: string) => void;
}

export default function VoiceRecordingInterface({ onCancel, onSave }: VoiceRecordingInterfaceProps) {
  const [duration, setDuration] = useState(0);
  const [isRecording, setIsRecording] = useState(true);
  const [audioData, setAudioData] = useState<number[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const MAX_DURATION = 60;

  useEffect(() => {
    startRecording();
    intervalRef.current = setInterval(() => {
      setDuration((prev) => {
        if (prev >= MAX_DURATION) {
          stopRecording();
          return MAX_DURATION;
        }
        return prev + 1;
      });
    }, 1000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      stopRecording();
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);

      const updateAudioData = () => {
        if (analyserRef.current && isRecording) {
          const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
          analyserRef.current.getByteTimeDomainData(dataArray);
          setAudioData(Array.from(dataArray));
          animationFrameRef.current = requestAnimationFrame(updateAudioData);
        }
      };
      updateAudioData();

      mediaRecorderRef.current = new MediaRecorder(stream);
      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };
      mediaRecorderRef.current.start();

    } catch (error) {
      console.error('Error starting recording:', error);
    }
  };

  const stopRecording = () => {
    setIsRecording(false);

    if (audioContextRef.current) {
      audioContextRef.current.close().catch(console.error);
      audioContextRef.current = null;
    }

    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }

    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => {
        track.stop();
        mediaStreamRef.current?.removeTrack(track);
      });
      mediaStreamRef.current = null;
    }
  };

  const handleSave = async () => {
    if (isProcessing) return; 

    setIsProcessing(true);
    stopRecording();

    await new Promise(resolve => setTimeout(resolve, 100));

    if (audioChunksRef.current.length > 0) {
      const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
      const formData = new FormData();
      formData.append('file', audioBlob, 'recording.webm');

      try {
        const response = await fetch('/api/transcribe', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error('Transcription failed');
        }

        const data = await response.json();
        onSave(data.transcript);
      } catch (error) {
        console.error('Error during transcription:', error);
      } finally {
        setIsProcessing(false);
      }
    } else {
      console.error('No audio data available');
      setIsProcessing(false);
    }
  };

  const handleCancel = () => {
    stopRecording();
    onCancel();
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <div
      ref={containerRef}
      className="flex items-center justify-between w-full p-2 rounded-lg z-20 bg-[hsl(var(--background))] border border-[hsl(var(--ring))] transition-shadow duration-200"
    >
      <Button variant="ghost" size="icon" onClick={handleCancel} className="rounded-full">
        <X className="size-4 text-[hsl(var(--foreground))]" />
      </Button>
      <div className="flex-1 mx-4">
        <Progress value={(duration / MAX_DURATION) * 100} className="w-full" />
      </div>
      <span className="text-sm text-[hsl(var(--foreground))] mr-4">{formatTime(duration)}</span>
      {isProcessing ? (
        <div className="w-8 h-8 flex items-center justify-center">
          <SpokeSpinner color="hsl(var(--primary))" />
        </div>
      ) : (
        <Button
          variant="ghost"
          size="icon"
          onClick={handleSave}
          className="rounded-full bg-[hsl(var(--primary))] hover:bg-[hsl(var(--primary))] hover:brightness-110 transition-all"
        >
          <Check className="size-4 text-[hsl(var(--primary-foreground))]" />
        </Button>
      )}
    </div>
  );
}   
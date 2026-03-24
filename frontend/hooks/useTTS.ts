'use client';

import { useMutation } from '@tanstack/react-query';
import { ttsService } from '@/services';
import { useRef } from 'react';

export function useTTS() {
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const mutation = useMutation({
    mutationFn: ttsService.synthesize,
    onSuccess: (data) => {
      if (audioRef.current) {
        audioRef.current.pause();
      }
      const audio = new Audio(data.audioUrl);
      audioRef.current = audio;
      audio.play();
    },
  });

  return {
    isSpeaking: mutation.isPending,
    speak: (text: string) => mutation.mutate({ text }),
    stop: () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    },
    error: mutation.error,
  };
}

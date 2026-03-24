'use client';

import { useMutation } from '@tanstack/react-query';
import { chatService } from '@/services';
import { useState, useCallback } from 'react';
import { generateId } from '@/utils';
import type { ChatMessage } from '@/types';

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const mutation = useMutation({
    mutationFn: chatService.send,
    onSuccess: (data) => {
      const assistantMessage: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        content: data.reply,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    },
  });

  const sendMessage = useCallback(
    (content: string) => {
      const userMessage: ChatMessage = {
        id: generateId(),
        role: 'user',
        content,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, userMessage]);

      const history = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      mutation.mutate({ message: content, history });
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [messages]
  );

  return {
    messages,
    isLoading: mutation.isPending,
    sendMessage,
    error: mutation.error,
    clearChat: () => setMessages([]),
  };
}

'use client';

import { useMutation } from '@tanstack/react-query';
import { nlpService } from '@/services';
import type { NLPInsightsResponse } from '@/types';

export function useSentiment() {
  const mutation = useMutation({
    mutationFn: (text: string) => nlpService.analyze({ text }),
  });

  return {
    analyze: (text: string) => mutation.mutate(text),
    result: mutation.data as NLPInsightsResponse | undefined,
    isLoading: mutation.isPending,
    error: mutation.error,
    reset: mutation.reset,
  };
}

'use client';

import { useMutation } from '@tanstack/react-query';
import { lemmatizeService } from '@/services';
import type { LemmatizeResponse } from '@/types';
import { useState } from 'react';

export function useLemmatize() {
  const [result, setResult] = useState<LemmatizeResponse | null>(null);

  const mutation = useMutation({
    mutationFn: lemmatizeService.lemmatize,
    onSuccess: (data) => setResult(data),
  });

  return {
    result,
    isLemmatizing: mutation.isPending,
    lemmatize: mutation.mutate,
    error: mutation.error,
    clearResult: () => setResult(null),
  };
}

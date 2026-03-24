'use client';

import { useMutation } from '@tanstack/react-query';
import { translateService } from '@/services';
import type { TranslateResponse } from '@/types';
import { useState } from 'react';

export function useTranslation() {
  const [result, setResult] = useState<TranslateResponse | null>(null);

  const mutation = useMutation({
    mutationFn: translateService.translate,
    onSuccess: (data) => setResult(data),
  });

  return {
    result,
    isTranslating: mutation.isPending,
    translate: mutation.mutate,
    error: mutation.error,
    clearResult: () => setResult(null),
  };
}

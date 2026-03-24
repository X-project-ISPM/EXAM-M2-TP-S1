'use client';

import { useMutation } from '@tanstack/react-query';
import { spellcheckService } from '@/services';
import { useDebounce } from './useDebounce';
import { useCallback, useState } from 'react';
import type { SpellError } from '@/types';

export function useSpellcheck() {
  const [errors, setErrors] = useState<SpellError[]>([]);

  const mutation = useMutation({
    mutationFn: spellcheckService.check,
    onSuccess: (data) => {
      setErrors(data.errors);
    },
    onError: () => {
      setErrors([]);
    },
  });

  const debouncedCheck = useDebounce(
    useCallback(
      (text: string) => {
        if (text.trim().length === 0) {
          setErrors([]);
          return;
        }
        mutation.mutate({ text });
      },
      // eslint-disable-next-line react-hooks/exhaustive-deps
      []
    ),
    500
  );

  return {
    errors,
    isChecking: mutation.isPending,
    checkSpelling: debouncedCheck,
    clearErrors: () => setErrors([]),
  };
}

'use client';

import { useCallback, useState } from 'react';
import { autocompleteService } from '@/services';
import { useDebounce } from './useDebounce';
import type { SpellError } from '@/types';

export function useSpellcheck() {
  const [errors, setErrors] = useState<SpellError[]>([]);
  const [isChecking, setIsChecking] = useState(false);

  const debouncedCheck = useDebounce(
    useCallback(
      async (text: string) => {
        if (text.trim().length === 0) {
          setErrors([]);
          return;
        }

        setIsChecking(true);
        try {
          // Vérifier chaque mot via l'endpoint autocomplete
          const words = text.match(/[a-zA-ZÀ-ÿ]+/g) || [];
          const found: SpellError[] = [];

          for (const word of words) {
            if (word.length < 2) continue;
            try {
              const res = await autocompleteService.suggest({ text: word, cursorPosition: word.length });
              // Si le type est "correction", le mot est mal orthographié
              if (res.type === 'correction') {
                const offset = text.indexOf(word);
                found.push({
                  word,
                  offset,
                  length: word.length,
                  suggestions: res.suggestions.map((s) => s.text),
                });
              }
            } catch {
              // Ignorer les erreurs réseau pour un mot
            }
          }

          setErrors(found);
        } catch {
          setErrors([]);
        } finally {
          setIsChecking(false);
        }
      },
      []
    ),
    500
  );

  return {
    errors,
    isChecking,
    checkSpelling: debouncedCheck,
    clearErrors: () => setErrors([]),
  };
}

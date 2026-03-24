'use client';

import { useMutation } from '@tanstack/react-query';
import { autocompleteService } from '@/services';
import { useState, useCallback } from 'react';
import { useDebounce } from './useDebounce';
import type { AutocompleteSuggestion } from '@/types';

export function useAutocomplete() {
  const [suggestions, setSuggestions] = useState<AutocompleteSuggestion[]>([]);
  const [suggestionType, setSuggestionType] = useState<'prediction' | 'correction'>('prediction');

  const mutation = useMutation({
    mutationFn: autocompleteService.suggest,
    onSuccess: (data) => {
      setSuggestions(data.suggestions);
      setSuggestionType(data.type || 'prediction');
    },
    onError: () => setSuggestions([]),
  });

  const debouncedSuggest = useDebounce(
    useCallback(
      (text: string, cursorPosition: number) => {
        if (text.trim().length === 0) {
          setSuggestions([]);
          return;
        }
        mutation.mutate({ text, cursorPosition });
      },
      // eslint-disable-next-line react-hooks/exhaustive-deps
      []
    ),
    300
  );

  return {
    suggestions,
    suggestionType,
    isLoading: mutation.isPending,
    getSuggestions: debouncedSuggest,
    clearSuggestions: () => setSuggestions([]),
  };
}

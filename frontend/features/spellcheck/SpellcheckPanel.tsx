'use client';

import type { SpellError } from '@/types';
import { Spinner } from '@/components/atoms';
import styles from './SpellcheckPanel.module.css';

interface SpellcheckPanelProps {
  errors: SpellError[];
  isChecking: boolean;
  onApplySuggestion?: (original: string, replacement: string) => void;
}

export function SpellcheckPanel({ errors, isChecking, onApplySuggestion }: SpellcheckPanelProps) {
  return (
    <div className={styles.panel}>
      <div className={styles.title}>
        Spell Check {isChecking && <Spinner size="sm" />}
      </div>

      {errors.length === 0 && !isChecking && (
        <p className={styles.empty}>No spelling issues found ✓</p>
      )}

      <div className={styles.errorList}>
        {errors.map((err, idx) => (
          <div key={`${err.word}-${idx}`} className={styles.errorItem}>
            <span className={styles.errorWord}>{err.word}</span>
            {err.suggestions.length > 0 && (
              <div className={styles.suggestions}>
                {err.suggestions.map((sug) => (
                  <button
                    key={sug}
                    className={styles.suggestionChip}
                    onClick={() => onApplySuggestion?.(err.word, sug)}
                    type="button"
                  >
                    {sug}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

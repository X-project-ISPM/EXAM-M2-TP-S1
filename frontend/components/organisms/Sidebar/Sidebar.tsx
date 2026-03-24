'use client';

import { useState } from 'react';
import { SpellcheckPanel } from '@/features/spellcheck';
import { TranslationPanel } from '@/features/translation';
import type { SpellError, LemmatizeResponse } from '@/types';
import { classNames } from '@/utils';
import styles from './Sidebar.module.css';

interface SidebarProps {
  spellErrors: SpellError[];
  isChecking: boolean;
  selectedText: string;
  lemmaResult: LemmatizeResponse | null;
  isVisible: boolean;
  onApplySuggestion?: (original: string, replacement: string) => void;
}

export function Sidebar({
  spellErrors,
  isChecking,
  selectedText,
  lemmaResult,
  isVisible,
  onApplySuggestion,
}: SidebarProps) {
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({
    spellcheck: true,
    translation: true,
    details: true,
  });

  const toggle = (key: string) =>
    setOpenSections((s) => ({ ...s, [key]: !s[key] }));

  return (
    <aside className={classNames(styles.sidebar, !isVisible && styles.hidden)}>
      {/* Spellcheck section */}
      <div className={styles.section}>
        <div className={styles.sectionHeader} onClick={() => toggle('spellcheck')}>
          <span className={styles.sectionTitle}>⚠ Spell Check</span>
          <span className={classNames(styles.sectionToggle, openSections.spellcheck && styles.open)}>
            ▶
          </span>
        </div>
        <div className={classNames(styles.sectionContent, openSections.spellcheck && styles.open)}>
          <SpellcheckPanel
            errors={spellErrors}
            isChecking={isChecking}
            onApplySuggestion={onApplySuggestion}
          />
        </div>
      </div>

      {/* Translation section */}
      <div className={styles.section}>
        <div className={styles.sectionHeader} onClick={() => toggle('translation')}>
          <span className={styles.sectionTitle}>🌐 Translation</span>
          <span className={classNames(styles.sectionToggle, openSections.translation && styles.open)}>
            ▶
          </span>
        </div>
        <div className={classNames(styles.sectionContent, openSections.translation && styles.open)}>
          <TranslationPanel initialText={selectedText} />
        </div>
      </div>

      {/* Word details section */}
      <div className={styles.section}>
        <div className={styles.sectionHeader} onClick={() => toggle('details')}>
          <span className={styles.sectionTitle}>📖 Word Details</span>
          <span className={classNames(styles.sectionToggle, openSections.details && styles.open)}>
            ▶
          </span>
        </div>
        <div className={classNames(styles.sectionContent, openSections.details && styles.open)}>
          {lemmaResult ? (
            <div>
              <div className={styles.detailItem}>
                <div className={styles.detailLabel}>Lemma</div>
                <div className={styles.detailValue}>{lemmaResult.lemma}</div>
              </div>
              <div className={styles.detailItem}>
                <div className={styles.detailLabel}>Part of Speech</div>
                <div className={styles.detailValue}>{lemmaResult.pos}</div>
              </div>
              {lemmaResult.morphology.length > 0 && (
                <div className={styles.detailItem}>
                  <div className={styles.detailLabel}>Morphology</div>
                  <div className={styles.detailValue}>{lemmaResult.morphology.join(', ')}</div>
                </div>
              )}
            </div>
          ) : (
            <p style={{ padding: '1rem', color: 'var(--color-text-muted)', fontSize: '0.8125rem', textAlign: 'center' }}>
              Select a word to see details
            </p>
          )}
        </div>
      </div>
    </aside>
  );
}

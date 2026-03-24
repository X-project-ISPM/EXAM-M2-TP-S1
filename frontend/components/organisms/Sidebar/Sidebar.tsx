'use client';

import { useState } from 'react';
import { SpellcheckPanel } from '@/features/spellcheck';
import { TranslationPanel } from '@/features/translation';
import type { SpellError } from '@/types';
import { classNames } from '@/utils';
import styles from './Sidebar.module.css';

interface SidebarProps {
  spellErrors: SpellError[];
  isChecking: boolean;
  selectedText: string;
  isVisible: boolean;
  onApplySuggestion?: (original: string, replacement: string) => void;
}

export function Sidebar({
  spellErrors,
  isChecking,
  selectedText,
  isVisible,
  onApplySuggestion,
}: SidebarProps) {
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({
    spellcheck: true,
    translation: true,
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
    </aside>
  );
}

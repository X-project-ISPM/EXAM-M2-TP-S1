'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
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
  textToTranslate?: string;
  onApplySuggestion?: (original: string, replacement: string) => void;
  onClose?: () => void;
}

export function Sidebar({
  spellErrors,
  isChecking,
  selectedText,
  isVisible,
  textToTranslate,
  onApplySuggestion,
  onClose,
}: SidebarProps) {
  const t = useTranslations('sidebar');
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({
    spellcheck: true,
    translation: true,
  });

  const toggle = (key: string) =>
    setOpenSections((s) => ({ ...s, [key]: !s[key] }));

  return (
    <>
      {isVisible && onClose && (
        <div className={styles.overlay} onClick={onClose} />
      )}
      <aside className={classNames(styles.sidebar, !isVisible && styles.hidden)}>
      {onClose && (
        <div className={styles.mobileHeader}>
          <button
            type="button"
            className={styles.mobileCloseButton}
            onClick={onClose}
            aria-label="Close sidebar"
          >
            ✕
          </button>
        </div>
      )}
      {/* Spellcheck section */}
      <div className={styles.section}>
        <div className={styles.sectionHeader} onClick={() => toggle('spellcheck')}>
          <span className={styles.sectionTitle}>{t('spellCheck')}</span>
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
          <span className={styles.sectionTitle}>{t('translation')}</span>
          <span className={classNames(styles.sectionToggle, openSections.translation && styles.open)}>
            ▶
          </span>
        </div>
        <div className={classNames(styles.sectionContent, openSections.translation && styles.open)}>
          <TranslationPanel initialText={selectedText} textToTranslate={textToTranslate} />
        </div>
      </div>
    </aside>
    </>
  );
}

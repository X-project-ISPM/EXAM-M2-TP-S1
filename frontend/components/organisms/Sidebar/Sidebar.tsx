'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { SpellcheckPanel } from '@/features/spellcheck';
import { TranslationPanel } from '@/features/translation';
import { SentimentPanel } from '@/features/sentiment';
import type { SpellError, NLPInsightsResponse } from '@/types';
import { classNames } from '@/utils';
import { IconChevronRight, IconX, IconCheckCircle, IconGlobe, IconBarChart } from '@/components/atoms/Icons';
import styles from './Sidebar.module.css';

interface SidebarProps {
  spellErrors: SpellError[];
  isChecking: boolean;
  selectedText: string;
  isVisible: boolean;
  textToTranslate?: string;
  onApplySuggestion?: (original: string, replacement: string) => void;
  onClose?: () => void;
  // sentiment
  sentimentResult?: NLPInsightsResponse;
  isSentimentLoading?: boolean;
  sentimentError?: unknown;
  onAnalyze?: () => void;
  editorText?: string;
}

export function Sidebar({
  spellErrors,
  isChecking,
  selectedText,
  isVisible,
  textToTranslate,
  onApplySuggestion,
  onClose,
  sentimentResult,
  isSentimentLoading = false,
  sentimentError,
  onAnalyze,
  editorText = '',
}: SidebarProps) {
  const t = useTranslations('sidebar');
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({
    spellcheck: true,
    translation: false,
    sentiment: true,
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
            <IconX size={16} />
          </button>
        </div>
      )}
      {/* Spellcheck section */}
      <div className={styles.section}>
        <div className={styles.sectionHeader} onClick={() => toggle('spellcheck')}>
          <div className={styles.sectionTitleGroup}>
            <IconCheckCircle size={13} className={styles.sectionIcon} />
            <span className={styles.sectionTitle}>{t('spellCheck')}</span>
          </div>
          <IconChevronRight size={13} className={classNames(styles.sectionToggle, openSections.spellcheck && styles.open)} />
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
          <div className={styles.sectionTitleGroup}>
            <IconGlobe size={13} className={styles.sectionIcon} />
            <span className={styles.sectionTitle}>{t('translation')}</span>
          </div>
          <IconChevronRight size={13} className={classNames(styles.sectionToggle, openSections.translation && styles.open)} />
        </div>
        <div className={classNames(styles.sectionContent, openSections.translation && styles.open)}>
          <TranslationPanel initialText={selectedText} textToTranslate={textToTranslate} />
        </div>
      </div>

      {/* Sentiment / NLP section */}
      <div className={styles.section}>
        <div className={styles.sectionHeader} onClick={() => toggle('sentiment')}>
          <div className={styles.sectionTitleGroup}>
            <IconBarChart size={13} className={styles.sectionIcon} />
            <span className={styles.sectionTitle}>{t('analysis')}</span>
          </div>
          <IconChevronRight size={13} className={classNames(styles.sectionToggle, openSections.sentiment && styles.open)} />
        </div>
        <div className={classNames(styles.sectionContent, openSections.sentiment && styles.open)}>
          <SentimentPanel
            result={sentimentResult}
            isLoading={isSentimentLoading}
            error={sentimentError}
            onAnalyze={onAnalyze ?? (() => {})}
            hasText={editorText.trim().length > 0}
          />
        </div>
      </div>
    </aside>
    </>
  );
}

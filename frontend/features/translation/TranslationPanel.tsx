'use client';

import { useState, useEffect, useRef } from 'react';
import { useTranslation } from '@/hooks';
import { useTranslations } from 'next-intl';
import { Button, Spinner } from '@/components/atoms';
import styles from './TranslationPanel.module.css';

interface TranslationPanelProps {
  initialText?: string;
  textToTranslate?: string;
}

export function TranslationPanel({ initialText = '', textToTranslate }: TranslationPanelProps) {
  const [text, setText] = useState(initialText);
  const [sourceLang, setSourceLang] = useState('mg');
  const [targetLang, setTargetLang] = useState('fr');
  const { result, isTranslating, translate } = useTranslation();
  const lastTranslated = useRef('');
  const t = useTranslations('translation');

  // Update text when initialText prop changes (selection change)
  useEffect(() => {
    if (initialText) setText(initialText);
  }, [initialText]);

  // Auto-translate when triggered from context menu or toolbar
  useEffect(() => {
    if (textToTranslate && textToTranslate !== lastTranslated.current) {
      lastTranslated.current = textToTranslate;
      setText(textToTranslate);
      translate({ text: textToTranslate, sourceLang, targetLang });
    }
  }, [textToTranslate, sourceLang, targetLang, translate]);

  const handleTranslate = () => {
    if (!text.trim()) return;
    translate({ text, sourceLang, targetLang });
  };

  return (
    <div className={styles.panel}>
      <div className={styles.title}>{t('title')}</div>

      <div className={styles.langRow}>
        <select
          className={styles.langSelect}
          value={sourceLang}
          onChange={(e) => setSourceLang(e.target.value)}
        >
          <option value="mg">{t('malagasy')}</option>
          <option value="fr">{t('french')}</option>
          <option value="en">{t('english')}</option>
        </select>
        <span className={styles.arrow}>→</span>
        <select
          className={styles.langSelect}
          value={targetLang}
          onChange={(e) => setTargetLang(e.target.value)}
        >
          <option value="fr">{t('french')}</option>
          <option value="mg">{t('malagasy')}</option>
          <option value="en">{t('english')}</option>
        </select>
      </div>

      <textarea
        className={styles.inputArea}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={t('placeholder')}
      />

      <Button onClick={handleTranslate} disabled={isTranslating || !text.trim()} size="sm">
        {isTranslating ? <Spinner size="sm" /> : t('translateBtn')}
      </Button>

      {result && (
        <div className={styles.resultBox}>{result.translatedText}</div>
      )}
    </div>
  );
}

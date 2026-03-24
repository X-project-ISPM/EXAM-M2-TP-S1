'use client';

import { useState } from 'react';
import { useTranslation } from '@/hooks';
import { Button, Spinner } from '@/components/atoms';
import styles from './TranslationPanel.module.css';

interface TranslationPanelProps {
  initialText?: string;
}

export function TranslationPanel({ initialText = '' }: TranslationPanelProps) {
  const [text, setText] = useState(initialText);
  const [sourceLang, setSourceLang] = useState('mg');
  const [targetLang, setTargetLang] = useState('fr');
  const { result, isTranslating, translate } = useTranslation();

  const handleTranslate = () => {
    if (!text.trim()) return;
    translate({ text, sourceLang, targetLang });
  };

  return (
    <div className={styles.panel}>
      <div className={styles.title}>Translation</div>

      <div className={styles.langRow}>
        <select
          className={styles.langSelect}
          value={sourceLang}
          onChange={(e) => setSourceLang(e.target.value)}
        >
          <option value="mg">Malagasy</option>
          <option value="fr">Français</option>
          <option value="en">English</option>
        </select>
        <span className={styles.arrow}>→</span>
        <select
          className={styles.langSelect}
          value={targetLang}
          onChange={(e) => setTargetLang(e.target.value)}
        >
          <option value="fr">Français</option>
          <option value="mg">Malagasy</option>
          <option value="en">English</option>
        </select>
      </div>

      <textarea
        className={styles.inputArea}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter text to translate..."
      />

      <Button onClick={handleTranslate} disabled={isTranslating || !text.trim()} size="sm">
        {isTranslating ? <Spinner size="sm" /> : 'Translate'}
      </Button>

      {result && (
        <div className={styles.resultBox}>{result.translatedText}</div>
      )}
    </div>
  );
}

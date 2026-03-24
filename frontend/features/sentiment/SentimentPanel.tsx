'use client';

import type { NLPInsightsResponse } from '@/types';
import { Spinner } from '@/components/atoms';
import { useTranslations } from 'next-intl';
import { IconSmile, IconFrown, IconMeh, IconTag, IconBarChart, IconAlertCircle } from '@/components/atoms/Icons';
import styles from './SentimentPanel.module.css';

interface SentimentPanelProps {
  result?: NLPInsightsResponse;
  isLoading: boolean;
  error?: unknown;
  onAnalyze: () => void;
  hasText: boolean;
}

function SentimentIcon({ label }: { label: string }) {
  const l = label.toLowerCase();
  if (l === 'positive' || l === 'positif' || l === 'positivo') return <IconSmile size={32} className={styles.sentimentIconPositive} />;
  if (l === 'negative' || l === 'négatif' || l === 'negatif' || l === 'négatif' || l === 'негативный') return <IconFrown size={32} className={styles.sentimentIconNegative} />;
  return <IconMeh size={32} className={styles.sentimentIconNeutral} />;
}

function normalizeLabel(label: string): 'positive' | 'negative' | 'neutral' {
  const l = label.toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '');
  if (l.startsWith('pos')) return 'positive';
  if (l.startsWith('neg')) return 'negative';
  return 'neutral';
}

function ScoreBar({ score }: { score: number }) {
  // score expected between -1 and 1, normalize to 0-100
  const pct = Math.round(((score + 1) / 2) * 100);
  const color =
    pct >= 60 ? 'var(--color-success)' : pct <= 40 ? 'var(--color-error)' : 'var(--color-warning)';
  return (
    <div className={styles.scoreBarWrap}>
      <div className={styles.scoreBarTrack}>
        <div className={styles.scoreBarFill} style={{ width: `${pct}%`, background: color }} />
      </div>
      <span className={styles.scoreLabel}>{score >= 0 ? '+' : ''}{score.toFixed(2)}</span>
    </div>
  );
}

export function SentimentPanel({ result, isLoading, error, onAnalyze, hasText }: SentimentPanelProps) {
  const t = useTranslations('sentiment');
  return (
    <div className={styles.panel}>
      <button
        className={styles.analyzeBtn}
        onClick={onAnalyze}
        disabled={isLoading || !hasText}
        type="button"
      >
        {isLoading ? (
          <>
            <Spinner size="sm" />
            <span>{t('analyzing')}</span>
          </>
        ) : (
          <>
            <IconBarChart size={15} />
            <span>{t('analyzeBtn')}</span>
          </>
        )}
      </button>

      {!!error && (
        <div className={styles.errorBox}>
          <IconAlertCircle size={15} />
          <span>{t('error')}</span>
        </div>
      )}

      {result && !isLoading && (
        <>
          {/* Sentiment */}
          <div className={styles.card}>
            <div className={styles.cardHeader}>
              <IconBarChart size={14} />
              <span>{t('sentiment')}</span>
            </div>
            <div className={styles.sentimentResult}>
              <SentimentIcon label={result.sentiment.label} />
              <div className={styles.sentimentInfo}>
                <span className={styles.sentimentLabel}>
                  {t(`label${normalizeLabel(result.sentiment.label).charAt(0).toUpperCase()}${normalizeLabel(result.sentiment.label).slice(1)}` as 'labelPositive' | 'labelNegative' | 'labelNeutral')}
                </span>
                <ScoreBar score={result.sentiment.score} />
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className={styles.statsRow}>
            <div className={styles.statChip}>
              <span className={styles.statValue}>{result.wordCount}</span>
              <span className={styles.statLabel}>{t('words')}</span>
            </div>
            <div className={styles.statChip}>
              <span className={styles.statValue}>{result.charCount}</span>
              <span className={styles.statLabel}>{t('chars')}</span>
            </div>
            <div className={styles.statChip}>
              <span className={styles.statValue}>{result.entities.length}</span>
              <span className={styles.statLabel}>{t('entities')}</span>
            </div>
          </div>

          {/* Entities */}
          {result.entities.length > 0 && (
            <div className={styles.card}>
              <div className={styles.cardHeader}>
                <IconTag size={14} />
                <span>{t('detectedEntities')}</span>
              </div>
              <div className={styles.entityList}>
                {result.entities.map((e, i) => (
                  <div key={i} className={styles.entityChip}>
                    <span className={styles.entityText}>{e.text}</span>
                    <span className={styles.entityLabel}>{e.label}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {!result && !isLoading && !error && (
        <p className={styles.empty}>{t('emptyHint')}</p>
      )}
    </div>
  );
}

'use client';

import { useLocale, useTranslations } from 'next-intl';
import { useTransition } from 'react';
import { setLocale } from '@/app/actions';
import type { Locale } from '@/i18n';
import { IconChevronRight } from '@/components/atoms/Icons';
import styles from './LocaleSwitcher.module.css';

const localeCodes: Record<string, string> = { mg: 'MG', fr: 'FR', en: 'EN' };

export function LocaleSwitcher() {
  const currentLocale = useLocale();
  const t = useTranslations('locale');
  const [isPending, startTransition] = useTransition();

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    startTransition(async () => {
      await setLocale(e.target.value as Locale);
      window.location.reload();
    });
  };

  return (
    <div className={styles.wrapper}>
      <span className={styles.code}>{localeCodes[currentLocale]}</span>
      <span className={styles.label}>{t(currentLocale as Locale)}</span>
      <select
        className={styles.select}
        value={currentLocale}
        onChange={handleChange}
        disabled={isPending}
        aria-label="Select language"
      >
        {(['mg', 'fr', 'en'] as const).map((loc) => (
          <option key={loc} value={loc}>
            {t(loc)}
          </option>
        ))}
      </select>
      <IconChevronRight size={11} className={styles.chevron} />
    </div>
  );
}

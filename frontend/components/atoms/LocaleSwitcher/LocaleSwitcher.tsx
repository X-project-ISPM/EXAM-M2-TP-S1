'use client';

import { useLocale, useTranslations } from 'next-intl';
import { useTransition } from 'react';
import { setLocale } from '@/app/actions';
import type { Locale } from '@/i18n';

const localeFlags: Record<string, string> = { mg: '🇲🇬', fr: '🇫🇷', en: '🇬🇧' };

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
    <select
      value={currentLocale}
      onChange={handleChange}
      disabled={isPending}
      style={{
        background: 'var(--color-surface, #1e1e2e)',
        color: 'var(--color-text, #cdd6f4)',
        border: '1px solid var(--color-border, #45475a)',
        borderRadius: '6px',
        padding: '4px 8px',
        fontSize: '0.8rem',
        cursor: 'pointer',
      }}
    >
      {(['mg', 'fr', 'en'] as const).map((loc) => (
        <option key={loc} value={loc}>
          {localeFlags[loc]} {t(loc)}
        </option>
      ))}
    </select>
  );
}

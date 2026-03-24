'use client';

import { useTranslations } from 'next-intl';
import { LocaleSwitcher } from '@/components/atoms';
import styles from './TopBar.module.css';

interface TopBarProps {
  onToggleSidebar: () => void;
  onToggleChat: () => void;
}

export function TopBar({ onToggleSidebar, onToggleChat }: TopBarProps) {
  const t = useTranslations('topBar');

  return (
    <header className={styles.topBar}>
      <div className={styles.left}>
        <span className={styles.logo}>
          {t('logo')}<span className={styles.logoAccent}>{t('logoAccent')}</span>
        </span>
      </div>

      <div className={styles.right}>
        <LocaleSwitcher />
        <button className={styles.iconBtn} onClick={onToggleChat} title={t('aiChat')} type="button">
          💬
        </button>
        <button className={styles.iconBtn} onClick={onToggleSidebar} title={t('toggleSidebar')} type="button">
          ☰
        </button>
        <div className={styles.avatar}>MG</div>
      </div>
    </header>
  );
}

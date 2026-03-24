'use client';

import styles from './TopBar.module.css';

interface TopBarProps {
  onToggleSidebar: () => void;
  onToggleChat: () => void;
}

export function TopBar({ onToggleSidebar, onToggleChat }: TopBarProps) {
  return (
    <header className={styles.topBar}>
      <div className={styles.left}>
        <span className={styles.logo}>
          Malagasy<span className={styles.logoAccent}>Editor</span>
        </span>
      </div>

      <div className={styles.right}>
        <button className={styles.iconBtn} onClick={onToggleChat} title="AI Chat" type="button">
          💬
        </button>
        <button className={styles.iconBtn} onClick={onToggleSidebar} title="Toggle Sidebar" type="button">
          ☰
        </button>
        <div className={styles.avatar}>MG</div>
      </div>
    </header>
  );
}

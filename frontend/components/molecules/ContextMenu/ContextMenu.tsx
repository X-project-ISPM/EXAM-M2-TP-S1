'use client';

import styles from './ContextMenu.module.css';

export interface ContextMenuItem {
  label: string;
  icon?: string;
  onClick: () => void;
}

interface ContextMenuProps {
  x: number;
  y: number;
  items: ContextMenuItem[];
  onClose: () => void;
}

export function ContextMenu({ x, y, items, onClose }: ContextMenuProps) {
  return (
    <>
      <div className={styles.overlay} onClick={onClose} />
      <div
        className={styles.menu}
        style={{ left: x, top: y }}
        role="menu"
      >
        {items.map((item, idx) => (
          <button
            key={idx}
            className={styles.menuItem}
            role="menuitem"
            onClick={() => {
              item.onClick();
              onClose();
            }}
            type="button"
          >
            {item.icon && <span className={styles.menuIcon}>{item.icon}</span>}
            {item.label}
          </button>
        ))}
      </div>
    </>
  );
}

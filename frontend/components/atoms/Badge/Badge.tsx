import styles from './Badge.module.css';
import { classNames } from '@/utils';
import { ReactNode } from 'react';

interface BadgeProps {
  variant?: 'info' | 'success' | 'warning' | 'error';
  children: ReactNode;
  className?: string;
}

export function Badge({ variant = 'info', children, className }: BadgeProps) {
  return (
    <span className={classNames(styles.badge, styles[variant], className)}>
      {children}
    </span>
  );
}

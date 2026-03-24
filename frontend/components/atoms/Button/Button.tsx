import { ButtonHTMLAttributes, ReactNode } from 'react';
import styles from './Button.module.css';
import { classNames } from '@/utils';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  children: ReactNode;
}

export function Button({
  variant = 'primary',
  size = 'md',
  className,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={classNames(styles.button, styles[variant], styles[size], className)}
      {...props}
    >
      {children}
    </button>
  );
}

import styles from './Spinner.module.css';
import { classNames } from '@/utils';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Spinner({ size = 'md', className }: SpinnerProps) {
  return <span className={classNames(styles.spinner, styles[size], className)} role="status" />;
}

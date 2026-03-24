'use client';

import { useState, useRef, useEffect } from 'react';
import { useChat } from '@/hooks';
import { useTranslations } from 'next-intl';
import { classNames } from '@/utils';
import { sanitizeText } from '@/utils';
import { IconChat, IconX } from '@/components/atoms/Icons';
import styles from './ChatPanel.module.css';

interface ChatPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ChatPanel({ isOpen, onClose }: ChatPanelProps) {
  const [input, setInput] = useState('');
  const { messages, isLoading, sendMessage } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const t = useTranslations('chat');

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;
    sendMessage(sanitizeText(trimmed));
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isOpen) return null;

  return (
    <div className={styles.chatPanel}>
      <div className={styles.header}>
        <span className={styles.headerTitle}>
          <IconChat size={15} />
          {t('title')}
        </span>
        <button onClick={onClose} className={styles.closeBtn} type="button" aria-label="Close">
          <IconX size={15} />
        </button>
      </div>

      <div className={styles.messages}>
        {messages.length === 0 && (
          <div className={styles.emptyState}>
            <IconChat size={32} className={styles.emptyIcon} />
            <span>{t('emptyState')}</span>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={classNames(
              styles.message,
              msg.role === 'user' ? styles.userMessage : styles.assistantMessage
            )}
          >
            {msg.content}
          </div>
        ))}

        {isLoading && <div className={styles.typing}>{t('typing')}</div>}
        <div ref={messagesEndRef} />
      </div>

      <div className={styles.inputArea}>
        <input
          className={styles.chatInput}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={t('inputPlaceholder')}
          disabled={isLoading}
        />
        <button
          className={styles.sendBtn}
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
          type="button"
        >
          ▶
        </button>
      </div>
    </div>
  );
}

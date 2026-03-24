'use client';

import { useState, useRef, useEffect } from 'react';
import { useChat } from '@/hooks';
import { classNames } from '@/utils';
import { sanitizeText } from '@/utils';
import styles from './ChatPanel.module.css';

interface ChatPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ChatPanel({ isOpen, onClose }: ChatPanelProps) {
  const [input, setInput] = useState('');
  const { messages, isLoading, sendMessage } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

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
        <span className={styles.headerTitle}>🤖 AI Assistant</span>
        <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.125rem', color: 'var(--color-text-muted)' }} type="button">
          ✕
        </button>
      </div>

      <div className={styles.messages}>
        {messages.length === 0 && (
          <div className={styles.emptyState}>
            <span className={styles.emptyIcon}>💬</span>
            <span>Ask me anything about Malagasy language!</span>
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

        {isLoading && <div className={styles.typing}>AI is typing...</div>}
        <div ref={messagesEndRef} />
      </div>

      <div className={styles.inputArea}>
        <input
          className={styles.chatInput}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
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

'use client';

import { useState, useCallback } from 'react';
import dynamic from 'next/dynamic';
import { useTranslations } from 'next-intl';
import { TopBar } from '@/components/organisms/TopBar';
import { Sidebar } from '@/components/organisms/Sidebar';
import { useSpellcheck, useSentiment } from '@/hooks';
import { IconChat } from '@/components/atoms/Icons';
import styles from './editor.module.css';

// Dynamic imports for heavy components
const EditorArea = dynamic(
  () => import('@/features/editor/EditorArea').then((m) => ({ default: m.EditorArea })),
  { ssr: false }
);

const ChatPanel = dynamic(
  () => import('@/features/chatbot/ChatPanel').then((m) => ({ default: m.ChatPanel })),
  { ssr: false }
);

export default function EditorPage() {
  const t = useTranslations('chat');
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [chatOpen, setChatOpen] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [textToTranslate, setTextToTranslate] = useState('');
  const [editorText, setEditorText] = useState('');

  const { errors: spellErrors, isChecking, checkSpelling } = useSpellcheck();
  const { analyze, result: sentimentResult, isLoading: isSentimentLoading, error: sentimentError } = useSentiment();

  const handleTextChange = useCallback(
    (text: string) => {
      setEditorText(text);
      checkSpelling(text);
    },
    [checkSpelling]
  );

  const handleSelectionChange = useCallback(
    (text: string) => {
      setSelectedText(text);
    },
    []
  );

  const handleAnalyze = useCallback(() => {
    const textToAnalyze = selectedText.trim() || editorText.trim();
    if (textToAnalyze) analyze(textToAnalyze);
  }, [selectedText, editorText, analyze]);

  return (
    <div className={styles.layout}>
      <TopBar
        onToggleSidebar={() => setSidebarVisible((v) => !v)}
        onToggleChat={() => setChatOpen((v) => !v)}
      />

      <div className={styles.body}>
        <main className={styles.mainArea}>
          <EditorArea
            onTextChange={handleTextChange}
            onSelectionChange={handleSelectionChange}
            onTranslate={(text) => setTextToTranslate(text)}
            onAnalyze={handleAnalyze}
          />
        </main>

        <Sidebar
          spellErrors={spellErrors}
          isChecking={isChecking}
          selectedText={selectedText}
          isVisible={sidebarVisible}
          textToTranslate={textToTranslate}
          onClose={() => setSidebarVisible(false)}
          sentimentResult={sentimentResult}
          isSentimentLoading={isSentimentLoading}
          sentimentError={sentimentError}
          onAnalyze={handleAnalyze}
          editorText={editorText}
        />

        {chatOpen && (
          <div className={styles.chatContainer}>
            <ChatPanel isOpen={chatOpen} onClose={() => setChatOpen(false)} />
          </div>
        )}
      </div>

      {/* Mobile chat FAB */}
      {!chatOpen && (
        <button
          className={styles.chatFab}
          onClick={() => setChatOpen(true)}
          type="button"
          aria-label={t('openChat')}
        >
          <IconChat size={20} />
        </button>
      )}
    </div>
  );
}

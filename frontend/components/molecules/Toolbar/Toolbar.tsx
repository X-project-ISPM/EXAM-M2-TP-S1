'use client';

import type { Editor } from '@tiptap/react';
import { useTranslations } from 'next-intl';
import styles from './Toolbar.module.css';
import { classNames } from '@/utils';

interface ToolbarProps {
  editor: Editor | null;
  onTranslate?: () => void;
  onTTS?: () => void;
  onAnalyze?: () => void;
}

export function Toolbar({ editor, onTranslate, onTTS, onAnalyze }: ToolbarProps) {
  const t = useTranslations('toolbar');
  if (!editor) return null;

  const btnClass = (isActive: boolean) =>
    classNames(styles.toolbarBtn, isActive && styles.active);

  return (
    <div className={styles.toolbar}>
      {/* Text formatting */}
      <div className={styles.group}>
        <button
          className={btnClass(editor.isActive('bold'))}
          onClick={() => editor.chain().focus().toggleBold().run()}
          title={t('bold')}
          type="button"
        >
          B
        </button>
        <button
          className={btnClass(editor.isActive('italic'))}
          onClick={() => editor.chain().focus().toggleItalic().run()}
          title={t('italic')}
          type="button"
        >
          <em>I</em>
        </button>
        <button
          className={btnClass(editor.isActive('underline'))}
          onClick={() => editor.chain().focus().toggleUnderline().run()}
          title={t('underline')}
          type="button"
        >
          <u>U</u>
        </button>
        <button
          className={btnClass(editor.isActive('strike'))}
          onClick={() => editor.chain().focus().toggleStrike().run()}
          title={t('strikethrough')}
          type="button"
        >
          <s>S</s>
        </button>
      </div>

      <span className={styles.divider} />

      {/* Heading */}
      <div className={styles.group}>
        <button
          className={btnClass(editor.isActive('heading', { level: 1 }))}
          onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
          title={t('heading1')}
          type="button"
        >
          H1
        </button>
        <button
          className={btnClass(editor.isActive('heading', { level: 2 }))}
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          title={t('heading2')}
          type="button"
        >
          H2
        </button>
      </div>

      <span className={styles.divider} />

      {/* Lists */}
      <div className={styles.group}>
        <button
          className={btnClass(editor.isActive('bulletList'))}
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          title={t('bulletList')}
          type="button"
        >
          &#8226;
        </button>
        <button
          className={btnClass(editor.isActive('orderedList'))}
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          title={t('orderedList')}
          type="button"
        >
          1.
        </button>
      </div>

      <span className={styles.divider} />

      {/* AI Actions */}
      <div className={styles.group}>
        {onTranslate && (
          <button className={styles.toolbarBtn} onClick={onTranslate} title={t('translate')} type="button">
            🌐
          </button>
        )}
        {onTTS && (
          <button className={styles.toolbarBtn} onClick={onTTS} title={t('tts')} type="button">
            🔊
          </button>
        )}
        {onAnalyze && (
          <button className={styles.toolbarBtn} onClick={onAnalyze} title={t('analyze')} type="button">
            🧠
          </button>
        )}
      </div>
    </div>
  );
}

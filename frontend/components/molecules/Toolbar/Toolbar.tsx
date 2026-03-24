'use client';

import type { Editor } from '@tiptap/react';
import styles from './Toolbar.module.css';
import { classNames } from '@/utils';

interface ToolbarProps {
  editor: Editor | null;
  onTranslate?: () => void;
  onLemmatize?: () => void;
  onTTS?: () => void;
  onAnalyze?: () => void;
}

export function Toolbar({ editor, onTranslate, onLemmatize, onTTS, onAnalyze }: ToolbarProps) {
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
          title="Bold"
          type="button"
        >
          B
        </button>
        <button
          className={btnClass(editor.isActive('italic'))}
          onClick={() => editor.chain().focus().toggleItalic().run()}
          title="Italic"
          type="button"
        >
          <em>I</em>
        </button>
        <button
          className={btnClass(editor.isActive('underline'))}
          onClick={() => editor.chain().focus().toggleUnderline().run()}
          title="Underline"
          type="button"
        >
          <u>U</u>
        </button>
        <button
          className={btnClass(editor.isActive('strike'))}
          onClick={() => editor.chain().focus().toggleStrike().run()}
          title="Strikethrough"
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
          title="Heading 1"
          type="button"
        >
          H1
        </button>
        <button
          className={btnClass(editor.isActive('heading', { level: 2 }))}
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          title="Heading 2"
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
          title="Bullet list"
          type="button"
        >
          &#8226;
        </button>
        <button
          className={btnClass(editor.isActive('orderedList'))}
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          title="Ordered list"
          type="button"
        >
          1.
        </button>
      </div>

      <span className={styles.divider} />

      {/* AI Actions */}
      <div className={styles.group}>
        {onTranslate && (
          <button className={styles.toolbarBtn} onClick={onTranslate} title="Translate selection" type="button">
            🌐
          </button>
        )}
        {onLemmatize && (
          <button className={styles.toolbarBtn} onClick={onLemmatize} title="Lemmatize selection" type="button">
            📖
          </button>
        )}
        {onTTS && (
          <button className={styles.toolbarBtn} onClick={onTTS} title="Text-to-Speech" type="button">
            🔊
          </button>
        )}
        {onAnalyze && (
          <button className={styles.toolbarBtn} onClick={onAnalyze} title="NLP Analysis" type="button">
            🧠
          </button>
        )}
      </div>
    </div>
  );
}

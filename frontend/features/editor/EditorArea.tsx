'use client';

import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import Underline from '@tiptap/extension-underline';
import Highlight from '@tiptap/extension-highlight';
import { useCallback, useState, useEffect, useMemo } from 'react';
import { useTranslations } from 'next-intl';
import { Toolbar } from '@/components/molecules/Toolbar';
import { ContextMenu } from '@/components/molecules/ContextMenu';
import type { ContextMenuItem } from '@/components/molecules/ContextMenu';
import { useSpellcheck, useAutocomplete, useTTS } from '@/hooks';
import { stripHtml } from '@/utils';
import type { EditorContextMenuState, AutocompleteSuggestion } from '@/types';
import styles from './EditorArea.module.css';

interface EditorAreaProps {
  onTextChange?: (text: string) => void;
  onSelectionChange?: (text: string) => void;
  onTranslate?: (text: string) => void;
}

export function EditorArea({ onTextChange, onSelectionChange, onTranslate }: EditorAreaProps) {
  const { errors: spellErrors, isChecking, checkSpelling } = useSpellcheck();
  const { suggestions, suggestionType, getSuggestions, clearSuggestions } = useAutocomplete();
  const { speak } = useTTS();
  const t = useTranslations();

  const [contextMenu, setContextMenu] = useState<EditorContextMenuState>({
    visible: false,
    x: 0,
    y: 0,
    selectedText: '',
  });

  const [showAutocomplete, setShowAutocomplete] = useState(false);
  const [autocompletePos, setAutocompletePos] = useState({ x: 0, y: 0 });

  const editor = useEditor({
    immediatelyRender: false,
    extensions: [
      StarterKit,
      Placeholder.configure({ placeholder: t('editor.placeholder') }),
      Underline,
      Highlight.configure({ multicolor: true }),
    ],
    content: '',
    onUpdate: ({ editor }) => {
      const text = stripHtml(editor.getHTML());
      onTextChange?.(text);
      checkSpelling(text);
    },
    onSelectionUpdate: ({ editor }) => {
      const { from, to } = editor.state.selection;
      if (from !== to) {
        const selectedText = editor.state.doc.textBetween(from, to, ' ');
        onSelectionChange?.(selectedText);
      }
    },
    editorProps: {
      attributes: {
        spellcheck: 'false',
        autocorrect: 'off',
        autocapitalize: 'off',
      },
      handleKeyDown: (_view, event) => {
        if (event.key === ' ' && editor) {
          const text = stripHtml(editor.getHTML());
          const pos = editor.state.selection.from;
          getSuggestions(text, pos);
          // Position will be set when suggestions arrive
          return false;
        }
        if (event.key === 'Escape') {
          setShowAutocomplete(false);
          clearSuggestions();
          return false;
        }
        return false;
      },
    },
  });

  // Show autocomplete popup when suggestions arrive
  useEffect(() => {
    if (suggestions.length > 0 && editor) {
      const coords = editor.view.coordsAtPos(editor.state.selection.from);
      setAutocompletePos({ x: coords.left, y: coords.bottom + 4 });
      setShowAutocomplete(true);
    } else {
      setShowAutocomplete(false);
    }
  }, [suggestions, editor]);

  const handleContextMenu = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      if (!editor) return;
      const { from, to } = editor.state.selection;
      const selectedText = from !== to ? editor.state.doc.textBetween(from, to, ' ') : '';
      setContextMenu({ visible: true, x: e.clientX, y: e.clientY, selectedText });
    },
    [editor]
  );

  const contextMenuItems = useMemo<ContextMenuItem[]>(() => {
    const text = contextMenu.selectedText;
    if (!text) return [];
    return [
      {
        label: t('contextMenu.translate'),
        icon: '🌐',
        onClick: () => onTranslate?.(text),
      },
      {
        label: t('contextMenu.listen'),
        icon: '🔊',
        onClick: () => speak(text),
      },
    ];
  }, [contextMenu.selectedText, onTranslate, speak]);

  const handleAutocompletePick = useCallback(
    (suggestion: AutocompleteSuggestion) => {
      if (!editor) return;
      const { from } = editor.state.selection;
      const textBefore = editor.state.doc.textBetween(0, from, '\0');

      if (suggestionType === 'correction') {
        // For corrections, replace the last word (skip trailing whitespace)
        const match = textBefore.match(/(\S+)\s*$/);
        if (match) {
          const wordEnd = textBefore.lastIndexOf(match[1]) + match[1].length;
          const wordStart = wordEnd - match[1].length;
          editor.chain().focus()
            .deleteRange({ from: wordStart, to: from })
            .insertContent(suggestion.text + ' ')
            .run();
        }
      } else {
        // For predictions, just insert the next word at cursor
        editor.chain().focus().insertContent(suggestion.text + ' ').run();
      }

      setShowAutocomplete(false);
      clearSuggestions();
    },
    [editor, clearSuggestions, suggestionType]
  );

  const handleToolbarTranslate = useCallback(() => {
    if (!editor) return;
    const { from, to } = editor.state.selection;
    if (from === to) return;
    const text = editor.state.doc.textBetween(from, to, ' ');
    onTranslate?.(text);
  }, [editor, onTranslate]);

  const handleToolbarTTS = useCallback(() => {
    if (!editor) return;
    const { from, to } = editor.state.selection;
    const text = from !== to ? editor.state.doc.textBetween(from, to, ' ') : stripHtml(editor.getHTML());
    speak(text);
  }, [editor, speak]);

  const wordCount = editor ? stripHtml(editor.getHTML()).split(/\s+/).filter(Boolean).length : 0;
  const charCount = editor ? stripHtml(editor.getHTML()).length : 0;

  return (
    <div className={styles.editorWrapper}>
      <Toolbar
        editor={editor}
        onTranslate={handleToolbarTranslate}
        onTTS={handleToolbarTTS}
      />

      <div className={styles.editorContent} onContextMenu={handleContextMenu}>
        <EditorContent editor={editor} />
      </div>

      {/* Autocomplete popup */}
      {showAutocomplete && suggestions.length > 0 && (
        <div
          className={styles.autocompletePopup}
          style={{ left: autocompletePos.x, top: autocompletePos.y, position: 'fixed' }}
        >
          {suggestions.map((s, idx) => (
            <button
              key={idx}
              className={styles.autocompleteItem}
              onClick={() => handleAutocompletePick(s)}
              type="button"
            >
              {s.text}
            </button>
          ))}
        </div>
      )}

      {/* Context menu */}
      {contextMenu.visible && contextMenu.selectedText && (
        <ContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          items={contextMenuItems}
          onClose={() => setContextMenu((s) => ({ ...s, visible: false }))}
        />
      )}

      {/* Status bar */}
      <div className={styles.statusBar}>
        <span>{wordCount} {t('editor.words')} &bull; {charCount} {t('editor.characters')}</span>
        <span>{isChecking ? t('editor.checkingSpelling') : `${spellErrors.length} ${spellErrors.length !== 1 ? t('editor.issues') : t('editor.issue')}`}</span>
      </div>
    </div>
  );
}

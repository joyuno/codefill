'use client';

import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import Editor, { OnMount } from '@monaco-editor/react';
import type { editor } from 'monaco-editor';

interface CodeEditorProps {
  initialCode: string;
  language?: string;
  onChange?: (code: string) => void;
  readOnly?: boolean;
}

// 언어별 파일 확장자 매핑
const languageExtensions: Record<string, string> = {
  python: 'py',
  javascript: 'js',
  typescript: 'ts',
  java: 'java',
  cpp: 'cpp',
  c: 'c',
};

export function CodeEditor({
  initialCode,
  language = 'python',
  onChange,
  readOnly = false,
}: CodeEditorProps) {
  const [code, setCode] = useState(initialCode);
  const [cursorPosition, setCursorPosition] = useState({ line: 1, column: 1 });
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);

  useEffect(() => {
    setCode(initialCode);
  }, [initialCode]);

  const handleEditorChange = (value: string | undefined) => {
    const newCode = value || '';
    setCode(newCode);
    onChange?.(newCode);
  };

  const handleEditorMount: OnMount = (editor) => {
    editorRef.current = editor;

    // 커서 위치 변경 추적
    editor.onDidChangeCursorPosition((e) => {
      setCursorPosition({
        line: e.position.lineNumber,
        column: e.position.column,
      });
    });

    // 에디터 포커스
    editor.focus();
  };

  const lines = code.split('\n').length;
  const fileExtension = languageExtensions[language] || language;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex h-full flex-col overflow-hidden rounded-lg bg-[#1e1e1e]"
    >
      {/* Editor header */}
      <div className="flex items-center gap-2 border-b border-[#333] bg-[#252526] px-4 py-2">
        <div className="flex gap-1.5">
          <div className="h-3 w-3 rounded-full bg-[#ff5f56]" />
          <div className="h-3 w-3 rounded-full bg-[#ffbd2e]" />
          <div className="h-3 w-3 rounded-full bg-[#27ca40]" />
        </div>
        <span className="ml-2 text-xs text-[#808080]">
          solution.{fileExtension}
        </span>
      </div>

      {/* Monaco Editor */}
      <div className="flex-1 min-h-0">
        <Editor
          height="100%"
          language={language}
          value={code}
          onChange={handleEditorChange}
          onMount={handleEditorMount}
          theme="vs-dark"
          options={{
            readOnly,
            minimap: { enabled: false },
            fontSize: 14,
            lineHeight: 24,
            padding: { top: 16, bottom: 16 },
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 4,
            wordWrap: 'on',
            folding: true,
            lineNumbers: 'on',
            renderLineHighlight: 'line',
            selectOnLineNumbers: true,
            roundedSelection: true,
            cursorStyle: 'line',
            cursorBlinking: 'smooth',
            smoothScrolling: true,
            contextmenu: true,
            fontFamily: "'Fira Code', 'Cascadia Code', Consolas, monospace",
            fontLigatures: true,
            bracketPairColorization: { enabled: true },
            guides: {
              indentation: true,
              bracketPairs: true,
            },
            suggest: {
              showKeywords: true,
              showSnippets: true,
              showClasses: true,
              showFunctions: true,
              showVariables: true,
            },
          }}
        />
      </div>

      {/* Status bar */}
      <div className="flex items-center justify-between border-t border-[#333] bg-[#007acc] px-4 py-1 text-xs text-white">
        <div className="flex items-center gap-4">
          <span>{language.charAt(0).toUpperCase() + language.slice(1)}</span>
          <span>UTF-8</span>
        </div>
        <div className="flex items-center gap-4">
          <span>Ln {cursorPosition.line}, Col {cursorPosition.column}</span>
          <span>{lines} lines</span>
          <span>{readOnly ? '읽기 전용' : '편집 가능'}</span>
        </div>
      </div>
    </motion.div>
  );
}

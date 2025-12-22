'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface CodeEditorProps {
  initialCode: string;
  language?: string;
  onChange?: (code: string) => void;
  readOnly?: boolean;
}

export function CodeEditor({
  initialCode,
  language = 'python',
  onChange,
  readOnly = false,
}: CodeEditorProps) {
  const [code, setCode] = useState(initialCode);

  useEffect(() => {
    setCode(initialCode);
  }, [initialCode]);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newCode = e.target.value;
    setCode(newCode);
    onChange?.(newCode);
  };

  const lines = code.split('\n');

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
          solution.{language === 'python' ? 'py' : language === 'javascript' ? 'js' : language}
        </span>
      </div>

      {/* Code area */}
      <div className="relative flex flex-1 overflow-hidden">
        {/* Line numbers */}
        <div className="flex flex-col bg-[#1e1e1e] px-2 py-4 text-right font-mono text-sm text-[#858585] select-none">
          {lines.map((_, i) => (
            <div key={i} className="leading-6 h-6">
              {i + 1}
            </div>
          ))}
        </div>

        {/* Text area */}
        <textarea
          value={code}
          onChange={handleChange}
          readOnly={readOnly}
          spellCheck={false}
          className={`flex-1 resize-none bg-transparent p-4 font-mono text-sm text-[#d4d4d4] leading-6 outline-none ${
            readOnly ? 'cursor-not-allowed opacity-70' : ''
          }`}
          style={{
            tabSize: 4,
            minHeight: '100%',
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
          <span>Ln {lines.length}, Col 1</span>
          <span>{readOnly ? '읽기 전용' : '편집 가능'}</span>
        </div>
      </div>
    </motion.div>
  );
}

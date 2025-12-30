'use client';

/**
 * ControlsGuide - 조작 가이드 UI
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { X, Gamepad2, Mouse } from 'lucide-react';

export function ControlsGuide() {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible) return null;

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      className="fixed left-4 top-1/2 -translate-y-1/2 z-40 pointer-events-auto"
    >
      <div
        className="p-4 rounded-xl text-sm"
        style={{
          background: 'rgba(0,0,0,0.7)',
          backdropFilter: 'blur(4px)',
        }}
      >
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-amber-200 font-bold flex items-center gap-2">
            <Gamepad2 className="w-4 h-4" />
            조작법
          </h3>
          <button
            onClick={() => setIsVisible(false)}
            className="text-gray-400 hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
        <div className="space-y-2 text-gray-300">
          <div className="flex items-center gap-2">
            <kbd className="px-2 py-1 bg-gray-700 rounded text-xs">WASD</kbd>
            <span>이동</span>
          </div>
          <div className="flex items-center gap-2">
            <kbd className="px-2 py-1 bg-gray-700 rounded text-xs">방향키</kbd>
            <span>이동</span>
          </div>
          <div className="flex items-center gap-2">
            <kbd className="px-2 py-1 bg-gray-700 rounded text-xs">SPACE</kbd>
            <span>심기/수확</span>
          </div>
          <div className="flex items-center gap-2">
            <Mouse className="w-4 h-4" />
            <span>클릭으로 심기/수확</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

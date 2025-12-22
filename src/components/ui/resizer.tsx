'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { cn } from '@/lib/utils';

interface ResizerProps {
  direction: 'horizontal' | 'vertical';
  onResize: (delta: number) => void;
  onResizeEnd?: () => void;
  className?: string;
}

export function Resizer({ direction, onResize, onResizeEnd, className }: ResizerProps) {
  const [isDragging, setIsDragging] = useState(false);
  const lastPosition = useRef<number>(0);

  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      setIsDragging(true);
      lastPosition.current = direction === 'horizontal' ? e.clientX : e.clientY;
    },
    [direction]
  );

  useEffect(() => {
    if (!isDragging) return;

    const handleMouseMove = (e: MouseEvent) => {
      const currentPosition = direction === 'horizontal' ? e.clientX : e.clientY;
      const delta = currentPosition - lastPosition.current;
      lastPosition.current = currentPosition;
      onResize(delta);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
      onResizeEnd?.();
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, direction, onResize, onResizeEnd]);

  return (
    <div
      className={cn(
        'group shrink-0 transition-colors',
        direction === 'horizontal'
          ? 'w-1 cursor-col-resize hover:bg-primary/50'
          : 'h-1 cursor-row-resize hover:bg-primary/50',
        isDragging && 'bg-primary',
        className
      )}
      onMouseDown={handleMouseDown}
    >
      <div
        className={cn(
          'opacity-0 group-hover:opacity-100 transition-opacity',
          direction === 'horizontal'
            ? 'w-1 h-full bg-primary/30'
            : 'h-1 w-full bg-primary/30',
          isDragging && 'opacity-100 bg-primary'
        )}
      />
    </div>
  );
}

interface ResizablePanelProps {
  children: React.ReactNode;
  defaultSize: number;
  minSize?: number;
  maxSize?: number;
  direction: 'left' | 'right';
  className?: string;
  onSizeChange?: (size: number) => void;
}

export function ResizablePanel({
  children,
  defaultSize,
  minSize = 200,
  maxSize = 800,
  direction,
  className,
  onSizeChange,
}: ResizablePanelProps) {
  const [size, setSize] = useState(defaultSize);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleResize = useCallback(
    (delta: number) => {
      setSize((prev) => {
        const newSize = direction === 'left' ? prev + delta : prev - delta;
        const clampedSize = Math.min(Math.max(newSize, minSize), maxSize);
        onSizeChange?.(clampedSize);
        return clampedSize;
      });
    },
    [direction, minSize, maxSize, onSizeChange]
  );

  return (
    <div
      ref={containerRef}
      className={cn('flex shrink-0', className)}
      style={{ width: size }}
    >
      {direction === 'right' && (
        <Resizer direction="horizontal" onResize={handleResize} />
      )}
      <div className="flex-1 overflow-hidden">{children}</div>
      {direction === 'left' && (
        <Resizer direction="horizontal" onResize={handleResize} />
      )}
    </div>
  );
}

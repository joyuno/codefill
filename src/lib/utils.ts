import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * LaTeX 전처리 함수 - \mbox 등을 KaTeX가 이해할 수 있는 형태로 변환
 * @param text LaTeX가 포함된 텍스트
 * @returns 전처리된 텍스트
 */
export function preprocessLatex(text: string): string {
  if (!text) return '';

  let processed = text;

  // \mbox{X} → \text{X} 변환 (KaTeX에서 \text가 더 잘 지원됨)
  processed = processed.replace(/\\mbox\{([^}]*)\}/g, '\\text{$1}');

  // \mboxX (중괄호 없는 경우) → \text{X} 변환
  // 예: \mbox0 → \text{0}, \mboxS → \text{S}
  processed = processed.replace(/\\mbox([A-Za-z0-9])/g, '\\text{$1}');

  // \texttt{X} 지원 보강
  processed = processed.replace(/\\texttt\{([^}]*)\}/g, '\\mathtt{$1}');

  return processed;
}

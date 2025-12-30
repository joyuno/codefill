/**
 * Solutions 관련 공통 상수
 * SolutionList, OfficialSolutions 등에서 공유
 */

export const languageConfig: Record<string, { label: string; color: string }> = {
  python: { label: 'Python', color: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
  java: { label: 'Java', color: 'bg-orange-500/20 text-orange-400 border-orange-500/30' },
  cpp: { label: 'C++', color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30' },
  c: { label: 'C', color: 'bg-gray-500/20 text-gray-400 border-gray-500/30' },
  javascript: { label: 'JavaScript', color: 'bg-yellow-400/20 text-yellow-300 border-yellow-400/30' },
  typescript: { label: 'TypeScript', color: 'bg-sky-500/20 text-sky-400 border-sky-500/30' },
};

export function getLanguageLabel(language: string): string {
  return languageConfig[language]?.label || language;
}

export function getLanguageColor(language: string): string {
  return languageConfig[language]?.color || '';
}

/**
 * Translation API Client
 * Azure Translator를 활용한 번역 API
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// 지원 언어 타입
export type LanguageCode = 'ko' | 'en' | 'ja' | 'zh-Hans' | 'zh-Hant' | 'es' | 'fr' | 'de' | 'pt' | 'ru' | 'vi' | 'th' | 'id';

export interface TranslateRequest {
  text: string;
  to_language: LanguageCode;
  from_language?: LanguageCode;
}

export interface TranslateResponse {
  success: boolean;
  translated_text?: string;
  detected_language?: string;
  to_language?: string;
  error?: string;
}

export interface DetectResponse {
  success: boolean;
  language?: string;
  language_name?: string;
  score?: number;
  error?: string;
}

export interface LanguagesResponse {
  languages: Record<string, string>;
}

/**
 * 텍스트 번역
 */
export async function translateText(
  text: string,
  toLanguage: LanguageCode,
  fromLanguage?: LanguageCode
): Promise<TranslateResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/translate/translate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        to_language: toLanguage,
        from_language: fromLanguage,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      return {
        success: false,
        error: error.detail || 'Translation failed',
      };
    }

    return await response.json();
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Network error',
    };
  }
}

/**
 * 언어 감지
 */
export async function detectLanguage(text: string): Promise<DetectResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/translate/detect`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      const error = await response.json();
      return {
        success: false,
        error: error.detail || 'Detection failed',
      };
    }

    return await response.json();
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Network error',
    };
  }
}

/**
 * 지원 언어 목록 조회
 */
export async function getSupportedLanguages(): Promise<LanguagesResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/translate/languages`);

    if (!response.ok) {
      throw new Error('Failed to fetch languages');
    }

    return await response.json();
  } catch (error) {
    // 기본 언어 목록 반환
    return {
      languages: {
        ko: '한국어',
        en: 'English',
        ja: '日本語',
        'zh-Hans': '简体中文',
        'zh-Hant': '繁體中文',
        es: 'Español',
        fr: 'Français',
        de: 'Deutsch',
      },
    };
  }
}

// 언어 표시 이름 (프론트엔드용)
export const LANGUAGE_LABELS: Record<LanguageCode, string> = {
  ko: '한국어',
  en: 'English',
  ja: '日本語',
  'zh-Hans': '简体中文',
  'zh-Hant': '繁體中文',
  es: 'Español',
  fr: 'Français',
  de: 'Deutsch',
  pt: 'Português',
  ru: 'Русский',
  vi: 'Tiếng Việt',
  th: 'ไทย',
  id: 'Indonesia',
};

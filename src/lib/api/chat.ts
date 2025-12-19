/**
 * Chat API Functions
 */

import { api } from './client';
import type { Message, QuickChip, Problem } from '../types';

export interface ChatRequest {
  message: string;
  sessionId?: string;
}

export interface ChatResponse {
  message: string;
  chips?: QuickChip[];
  problems?: Problem[];
  sessionId: string;
  action?: {
    type: 'navigate' | 'show_problem' | 'show_code';
    payload?: unknown;
  };
}

export interface CodeSearchResult {
  id: string;
  title: string;
  framework: string;
  snippet: string;
  relevance: number;
  url?: string;
}

export interface SearchResponse {
  results: CodeSearchResult[];
  total: number;
}

export const chatApi = {
  /**
   * Send a chat message
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await api.post<ChatResponse>('/chat', {
      message: request.message,
      session_id: request.sessionId,
    });
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Search code snippets using RAG
   */
  async searchCode(query: string, limit: number = 5): Promise<SearchResponse> {
    const response = await api.post<SearchResponse>('/chat/search', {
      query,
      limit,
    });
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Get chat history for a session
   */
  async getHistory(sessionId: string): Promise<Message[]> {
    const response = await api.get<Message[]>(`/chat/history/${sessionId}`);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * Clear chat history for a session
   */
  async clearHistory(sessionId: string): Promise<void> {
    const response = await api.delete<void>(`/chat/history/${sessionId}`);
    if (response.error) throw new Error(response.error.message);
  },
};

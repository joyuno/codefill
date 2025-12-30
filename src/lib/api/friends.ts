/**
 * Friends API Client
 * 친구 시스템 (친구 요청, 수락/거부, 1:1 메시지)
 */

import { api } from './client';

// =====================================================
// Types
// =====================================================

export interface FriendRequest {
  id: string;
  requester_id: string;
  requester_name: string | null;
  requester_avatar: string | null;
  created_at: string;
}

export interface Friend {
  user_id: string;
  name: string | null;
  avatar_url: string | null;
  friendship_id: string;
  since: string;
  is_blocked: boolean;
  unread_count: number;
  last_message: string | null;
  last_message_at: string | null;
  last_message_is_mine: boolean | null;
}

export interface FriendListResponse {
  friends: Friend[];
  total: number;
}

export interface FriendRequestsResponse {
  requests: FriendRequest[];
  total: number;
}

export interface SentRequest {
  id: string;
  addressee_id: string;
  addressee_name: string | null;
  addressee_avatar: string | null;
  created_at: string;
}

export interface SentRequestsResponse {
  requests: SentRequest[];
  total: number;
}

export interface Message {
  id: string;
  sender_id: string;
  sender_name: string | null;
  sender_avatar: string | null;
  content: string;
  is_read: boolean;
  is_mine: boolean;
  created_at: string;
}

export interface ConversationResponse {
  messages: Message[];
  friend: Friend;
  has_more: boolean;
}

export interface UserSearchResult {
  id: string;
  name: string | null;
  avatar_url: string | null;
  friendship_status: 'pending' | 'accepted' | 'blocked' | null;
}

export interface UserSearchResponse {
  users: UserSearchResult[];
  total: number;
}

export interface UnreadCountResponse {
  pending_requests: number;
  unread_messages: number;
  total: number;
}

// =====================================================
// API Functions
// =====================================================

export const friendsApi = {
  /**
   * 친구 목록 조회
   */
  async listFriends(): Promise<FriendListResponse> {
    const response = await api.get<FriendListResponse>('/friends');
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 받은 친구 요청 목록
   */
  async listRequests(): Promise<FriendRequestsResponse> {
    const response = await api.get<FriendRequestsResponse>('/friends/requests');
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 보낸 친구 요청 목록
   */
  async listSentRequests(): Promise<SentRequestsResponse> {
    const response = await api.get<SentRequestsResponse>('/friends/requests/sent');
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 미확인 알림 수 조회
   */
  async getUnreadCounts(): Promise<UnreadCountResponse> {
    const response = await api.get<UnreadCountResponse>('/friends/counts');
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 친구 요청 보내기
   */
  async sendRequest(userId: string): Promise<{ message: string; status: string }> {
    const response = await api.post<{ message: string; status: string }>(`/friends/request/${userId}`, {});
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 친구 요청 수락
   */
  async acceptRequest(friendshipId: string): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>(`/friends/${friendshipId}/accept`, {});
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 친구 요청 거부 또는 친구 삭제
   */
  async deleteFriendship(friendshipId: string): Promise<{ message: string }> {
    const response = await api.delete<{ message: string }>(`/friends/${friendshipId}`);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 유저 차단
   */
  async blockUser(userId: string): Promise<{ message: string }> {
    const response = await api.post<{ message: string }>(`/friends/${userId}/block`, {});
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 차단 해제
   */
  async unblockUser(userId: string): Promise<{ message: string }> {
    const response = await api.delete<{ message: string }>(`/friends/${userId}/block`);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 유저 검색
   */
  async searchUsers(query: string): Promise<UserSearchResponse> {
    const response = await api.get<UserSearchResponse>(`/friends/search?q=${encodeURIComponent(query)}`);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 대화 내역 조회
   */
  async getConversation(userId: string, page = 1): Promise<ConversationResponse> {
    const response = await api.get<ConversationResponse>(`/friends/messages/${userId}?page=${page}`);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 메시지 전송
   */
  async sendMessage(userId: string, content: string): Promise<Message> {
    const response = await api.post<Message>(`/friends/messages/${userId}`, { content });
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 메시지 읽음 처리
   */
  async markAsRead(userId: string): Promise<{ message: string }> {
    const response = await api.put<{ message: string }>(`/friends/messages/${userId}/read`, {});
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },

  /**
   * 메시지 삭제
   */
  async deleteMessage(messageId: string): Promise<{ message: string }> {
    const response = await api.delete<{ message: string }>(`/friends/messages/${messageId}`);
    if (response.error) throw new Error(response.error.message);
    return response.data!;
  },
};

import { backendHost } from '@/app/utils/sharedConfig';

// BACKEND API URLS
const API_BASE_URL = backendHost;
const CREATE_CONVERSATION_URL = `${API_BASE_URL}/ask/conversation`;
const ASK_STREAM_URL = `${API_BASE_URL}/ask/response/stream`;
const getConversationFeedbackUrl = (conversationId: string): string => {
  return `${API_BASE_URL}/ask/${conversationId}/feedback`;
};


// FETCH API FUNCTIONS
export interface ConversationResponse {
  conversation_id: string;
}

export const createConversationAPI = async (): Promise<ConversationResponse> => {
  const response = await fetch(CREATE_CONVERSATION_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  });

  if (!response.ok) {
    const errorBody = await response.text().catch(() => 'Failed to read error body');
    throw new Error(`Could not create new conversation: ${response.status} - ${errorBody}`);
  }
  return response.json() as Promise<ConversationResponse>;
};

// SSE HELPERS
export const getChunkTextFromSSE = (chunk: string | number | boolean | { text?: unknown; message?: string; content?: string; response?: string; } | null | undefined): string =>  {
  if (chunk === null || chunk === undefined) return '';
  if (typeof chunk === 'string') return chunk;
  if (typeof chunk === 'object') {
    if (typeof chunk.text === 'string') return chunk.text;
    if (typeof chunk.message === 'string') return chunk.message;
    if (typeof chunk.content === 'string') return chunk.content;
    if (typeof chunk.response === 'string') return chunk.response;
    if (chunk.text !== undefined) return String(chunk.text);
    return '';
  }
  if (typeof chunk === 'number' || typeof chunk === 'boolean') {
    return String(chunk);
  }
  return '';
};


// STREAMING API
export interface AskStreamPayload {
  conversation_id: string;
  query: string;
}

export const fetchChatResponseStreamAPI = async (
  payload: AskStreamPayload,
  signal: AbortSignal
): Promise<Response> => { 
  const response = await fetch(ASK_STREAM_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
    },
    body: JSON.stringify(payload),
    signal: signal,
  });

  if (!response.ok) {
    const errorBody = await response.text().catch(() => 'Failed to read error body');
    throw new Error(`Server error for streaming: ${response.status} ${response.statusText} - ${errorBody}`);
  }
  if (!response.body) {
    throw new Error('Response body is null for streaming.');
  }
  return response; 
};

// FEEDBACK API
export type FeedbackVotePayload = 'positive' | 'negative' | 'not_specified';

export interface FeedbackPayload {
  vote: FeedbackVotePayload;
  comment: string;
}

export const submitFeedbackAPI = async (
  conversationId: string,
  payload: FeedbackPayload
): Promise<void> => { 
  const actualEndpoint = getConversationFeedbackUrl(conversationId);
  const response = await fetch(actualEndpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: 'Failed to parse error JSON.' }));
    throw new Error(`Server error on feedback: ${response.status} - ${errorData.message || response.statusText}`);
  }
};
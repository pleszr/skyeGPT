import { getBackendHost } from '@/app/utils/sharedConfig';

const cachedBackendHostPromise = getBackendHost();

// FETCH API FUNCTIONS
export interface ConversationResponse {
  conversation_id: string;
}

export const createConversationAPI = async (): Promise<ConversationResponse> => {
  const backendHost = await cachedBackendHostPromise;
  const CREATE_CONVERSATION_URL = `${backendHost}/ask/conversation`;

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
  return await response.json() as Promise<ConversationResponse>;
};

// SSE HELPERS
export const getChunkTextFromSSE = (
  chunk:
    | string
    | number
    | boolean
    | { text?: unknown; message?: string; content?: string; response?: string }
    | null
    | undefined
): string => {
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
  if (typeof chunk === 'number' || true) {
    return String(chunk);
  }
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
  const backendHost = await cachedBackendHostPromise;
  const ASK_STREAM_URL = `${backendHost}/ask/response/stream`;

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
    throw new Error(
      `Server error for streaming: ${response.status} ${response.statusText} - ${errorBody}`
    );
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

// Helper to get feedback URL
export const getConversationFeedbackUrl = async (conversationId: string): Promise<string> => {
  const backendHost = await cachedBackendHostPromise;
  return `${backendHost}/ask/${conversationId}/feedback`;
};

export const submitFeedbackAPI = async (
  conversationId: string,
  payload: FeedbackPayload
): Promise<void> => {
  const actualEndpoint = await getConversationFeedbackUrl(conversationId);

  const response = await fetch(actualEndpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({
      message: 'Failed to parse error JSON.',
    }));
    throw new Error(
      `Server error on feedback: ${response.status} - ${errorData.message || response.statusText}`
    );
  }
};

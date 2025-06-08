import { render, screen, act, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChatBox, { ChatBoxProps } from '@/app/components/chatBox';
import HomePage from '@/app/page';
import { describe, vi, it, beforeEach, expect, beforeAll, MockedFunction } from 'vitest';
import * as chatApiService from '@/app/services/chatApiService';
import { v4 as uuidv4 } from 'uuid'; 

vi.mock('@/app/services/chatApiService', () => ({
  createConversationAPI: vi.fn(),
  fetchChatResponseStreamAPI: vi.fn(),
  submitFeedbackAPI: vi.fn(),
  getChunkTextFromSSE: vi.fn(chunk => (typeof chunk === 'string' ? chunk : (chunk as any)?.text || '')),
}));

vi.mock('@/app/utils/sharedConfig', () => ({
  getConfig: vi.fn().mockResolvedValue({
    backendHost: 'http://localhost:8000',
    version: '0.0.0' // FOR TESTING PURPOSES
  }),
  getBackendHost: vi.fn().mockResolvedValue('http://localhost:8000'),
  getVersion: vi.fn().mockResolvedValue('0.0.0') // FOR TESTING PURPOSES
}));

const mockedCreateConversationAPI = chatApiService.createConversationAPI as MockedFunction<typeof chatApiService.createConversationAPI>;
const mockedFetchChatResponseStreamAPI = chatApiService.fetchChatResponseStreamAPI as MockedFunction<typeof chatApiService.fetchChatResponseStreamAPI>;

const MOCK_CONVERSATION_ID: string = uuidv4();

global.AbortController = vi.fn(() => ({
  signal: { aborted: false, addEventListener: vi.fn(), removeEventListener: vi.fn(), dispatchEvent: vi.fn(), onabort: vi.fn() },
  abort: vi.fn(),
})) as any;

beforeAll(() => {
  Object.defineProperty(window.HTMLElement.prototype, 'scrollTo', {
    configurable: true,
    value: vi.fn(),
  });
  window.alert = vi.fn();
});

const getDefaultChatBoxProps = (overrideProps: Partial<ChatBoxProps> = {}): ChatBoxProps => {
  return {
    messages: [],
    setMessages: vi.fn(),
    className: '',
    conversationId: MOCK_CONVERSATION_ID,
    ...overrideProps,
  };
};

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.setItem('conversation_id', MOCK_CONVERSATION_ID);
  mockedCreateConversationAPI.mockResolvedValue({ conversation_id: MOCK_CONVERSATION_ID });
});

describe('Application Smoke Tests', () => {
  it('ChatBox renders with initial message when no messages are provided', () => {
    const props = getDefaultChatBoxProps({ messages: [] });
    render(<ChatBox {...props} />);
    expect(screen.getByPlaceholderText('Write your question here...')).toBeInTheDocument();
    expect(screen.getByTitle('Send')).toBeInTheDocument();
  });

  it('Testing stop streaming', async () => {
    let abortHandler: (() => void) | undefined;
    mockedFetchChatResponseStreamAPI.mockImplementation((_payload, signal) => {
      if (signal) {
        signal.addEventListener?.('abort', () => {
          abortHandler?.();
        });
      }
      return new Promise((_resolve, _reject) => {
        abortHandler = () => {};
      });
    });

    render(<ChatBox {...getDefaultChatBoxProps()} />); 

    const textarea = screen.getByPlaceholderText('Write your question here...') as HTMLTextAreaElement;
    const sendButton = screen.getByTitle('Send') as HTMLButtonElement;

    expect(textarea).not.toBeDisabled();
    expect(sendButton).toBeDisabled();

    await userEvent.type(textarea, 'SkyeGPT');
    await waitFor(() => expect(sendButton).not.toBeDisabled());

    await userEvent.click(sendButton);

    await waitFor(() => {
      expect(textarea).toBeDisabled();
      expect(screen.getByTitle('Stop')).toBeInTheDocument();
    });

    const stopButton = screen.getByTitle('Stop');
    await userEvent.click(stopButton);

    await waitFor(() => {
      expect(textarea).not.toBeDisabled();
      expect(screen.getByTitle('Send')).toBeInTheDocument();
    });
  });

  it('HomePage renders, displays logo, and initializes conversation with the mock ID', async () => {
    render(<HomePage />);
    
    await waitFor(() => {
      expect(mockedCreateConversationAPI).toHaveBeenCalled();
    });

    const logos = screen.getAllByAltText('SkyeGPT logo');
    expect(logos.length).toBeGreaterThan(0);
    logos.forEach(logo => expect(logo).toBeInTheDocument());
    
    expect(localStorage.getItem('conversation_id')).toBe(MOCK_CONVERSATION_ID);
  });
});
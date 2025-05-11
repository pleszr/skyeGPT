import { render, screen, act, waitFor, fireEvent } from '@testing-library/react'; 
import ChatBox, { ChatBoxProps } from '@/app/components/chatBox';
import { describe, vi, it, beforeEach, expect, beforeAll } from 'vitest';
import HomePage from '@/app/page';

global.fetch = vi.fn(() => Promise.resolve(new Response(JSON.stringify({ conversation_id: 'mock-id' }), {
  status: 200,
  headers: { 'Content-Type': 'application/json' }
})));

global.AbortController = vi.fn(() => ({
  signal: { aborted: false, addEventListener: vi.fn(), removeEventListener: vi.fn(), dispatchEvent: vi.fn(), onabort: vi.fn() },
  abort: vi.fn(),
})) as any;

beforeAll(() => {
  Object.defineProperty(window.HTMLElement.prototype, 'scrollTo', {
    configurable: true,
    value: function () {},
  });
});

const getDefaultChatBoxProps = (overrideProps: Partial<ChatBoxProps> = {}): ChatBoxProps => ({
  messages: [],
  setMessages: vi.fn(),
  askEndpoint: '/api/ask',
  className: '',
  ...overrideProps,
});

beforeEach(() => {
  vi.clearAllMocks();
  global.fetch = vi.fn(() => Promise.resolve(new Response(JSON.stringify({ conversation_id: 'mock-id' }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  })));
  localStorage.clear();
  localStorage.setItem('chroma_conversation_id', 'test-smoke-convo-id');
});

describe('ChatBox Component Tests', () => { 
  it('shows empty state when there are no messages and component is not actively loading', () => {
    const props = getDefaultChatBoxProps({ messages: [] });
    render(<ChatBox {...props} />);
    expect(screen.getByText('No messages yet.')).toBeInTheDocument();
    expect(screen.getByText('Start the conversation below!')).toBeInTheDocument();
  });

  it('enables send button after typing and disables controls during message send', async () => {
    render(<ChatBox {...getDefaultChatBoxProps()} />);

    const textarea = screen.getByPlaceholderText('Write your question here...') as HTMLTextAreaElement;
    const sendButtonInitially = screen.getByTitle('Send') as HTMLButtonElement;

    expect(textarea).not.toBeDisabled();
    expect(sendButtonInitially).toBeDisabled();

    fireEvent.change(textarea, { target: { value: 'SkyeGPT' } });

    await waitFor(() => {
      const sendButtonAfterTyping = screen.getByTitle('Send') as HTMLButtonElement;
      expect(sendButtonAfterTyping).not.toBeDisabled();
    });

    global.fetch = vi.fn(() => new Promise<Response>(() => {}));

    const sendButtonEnabled = screen.getByTitle('Send') as HTMLButtonElement;
    await act(async () => {
      sendButtonEnabled.click();
    });

    const textareaAfterClick = screen.getByPlaceholderText('Write your question here...') as HTMLTextAreaElement;
    const sendButtonAfterClick = screen.getByTitle('Send') as HTMLButtonElement;

    expect(textareaAfterClick).toBeDisabled();
    expect(sendButtonAfterClick).toBeDisabled();
  });

  it('displays the logo on HomePage', () => {
    render(<HomePage />);
    const logos = screen.getAllByAltText('SkyeGPT logo');
    expect(logos.length).toBeGreaterThan(0);
    logos.forEach(logo => expect(logo).toBeInTheDocument());
  });
});
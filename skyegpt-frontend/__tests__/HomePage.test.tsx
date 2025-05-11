import { render, screen } from '@testing-library/react';
import HomePage from '@/app/page';
import { describe, vi, it, beforeEach, expect } from 'vitest';
import ChatBox from '@/app/components/chatBox';

global.fetch = vi.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ thread_id: 'mock-thread', chroma_conversation_id: 'mock-chroma' }),
  } as Response)
);

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
});

describe('HomePage', () => {
  it('shows empty state when there are no messages and not loading', () => {
    const props = {
      messages: [],
      isLoading: false,
      className: '',
      chatContainerRef: { current: null },
      askEndpoint: '/api/ask',
      setMessages: vi.fn(),
    };


    render(<ChatBox {...props} />);
    expect(screen.getByText('No messages yet.')).toBeInTheDocument();
    expect(screen.getByText('Start the conversation below!')).toBeInTheDocument();
  });

  it('displays the logo', () => {
    render(<HomePage />);
    const logos = screen.getAllByAltText('SkyeGPT logo');
    expect(logos.length).toBeGreaterThan(0);
    logos.forEach(logo => expect(logo).toBeInTheDocument());
  });


});
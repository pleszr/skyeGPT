import { render, screen } from '@testing-library/react';
import HomePage from '@/app/page';
import { describe, vi, it, beforeEach, expect } from 'vitest';

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
  it('renders without crashing', () => {
    render(<HomePage />);
    expect(screen.getByText('Ask Skye Documentation')).toBeInTheDocument();
  });

  it('displays the logo', () => {
    render(<HomePage />);
    const logo = screen.getByAltText('logo');
    expect(logo).toBeInTheDocument();
  });

  it('has NEXT_PUBLIC_SKYEGPT_BACKEND_HOST set to the correct backend value', () => {
    expect(process.env.NEXT_PUBLIC_SKYEGPT_BACKEND_HOST).toBe('http://localhost:8000');
  });
});
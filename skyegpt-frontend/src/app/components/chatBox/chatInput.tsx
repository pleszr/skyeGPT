'use client';

import React, { useRef, useEffect, useCallback } from 'react';
import Image from 'next/image';

const INITIAL_TEXTAREA_CONTENT_HEIGHT_PX_STR = '98px';
const MAX_TEXTAREA_HEIGHT_PX = 98;

interface ChatInputProps {
  input: string;
  setInput: (value: string) => void;
  isLoading: boolean;
  onSend: () => void;
  onStop: () => void;
}

const ChatInput: React.FC<ChatInputProps> = ({
  input,
  setInput,
  isLoading,
  onSend,
  onStop
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const textareaResize = useCallback(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const newScrollHeight = textarea.scrollHeight;
      textarea.style.height = `${Math.min(newScrollHeight, MAX_TEXTAREA_HEIGHT_PX)}px`;
    }
  }, []);

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && input.trim() && !isLoading) {
      e.preventDefault();
      onSend();
    }
  }, [input, isLoading, onSend]);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.focus();
      textarea.style.height = INITIAL_TEXTAREA_CONTENT_HEIGHT_PX_STR;
      textareaResize();
      textarea.addEventListener('input', textareaResize);
    }
    return () => {
      if (textarea) textarea.removeEventListener('input', textareaResize);
    };
  }, [textareaResize]);

  useEffect(() => {
    if (!isLoading && textareaRef.current) {
      const focusTimeoutId = setTimeout(() => {
        if (textareaRef.current && document.activeElement !== textareaRef.current) {
          textareaRef.current.focus();
        }
      }, 50);
      return () => clearTimeout(focusTimeoutId);
    }
  }, [isLoading]);

  return (
    <div className="flex items-center p-2 sm:p-3 gap-2 sm:gap-3 border-t border-gray-200 bg-white shrink-0">
      <div className="flex-1 bg-gray-100 rounded-[20px] transition-all duration-200 shadow-sm flex items-end">
        <textarea
          ref={textareaRef}
          rows={1}
          className="border-none text-sm sm:text-base text-black resize-none bg-transparent w-full py-2 px-3 font-[Poppins] placeholder:text-gray-500 focus:outline-none"
          style={{ minHeight: INITIAL_TEXTAREA_CONTENT_HEIGHT_PX_STR }}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onInput={textareaResize}
          placeholder="Write your question here..."
          disabled={isLoading}
          aria-label="Chat input"
        />
      </div>
      <button
        className="skgpt-btn sendBtn p-0 border-none bg-transparent cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center shrink-0 hover:opacity-80 transition-opacity"
        onClick={isLoading ? onStop : onSend}
        disabled={!isLoading && !input.trim()}
        title={isLoading ? "Stop" : "Send"}
        aria-label={isLoading ? "Stop message" : "Send message"}
      >
        <Image
          src={isLoading ? "/stop.png" : "/button.png"}
          alt={isLoading ? "Stop" : "Send"}
          width={120}
          height={120}
          quality={100}
          style={{ width: 'auto', height: 'auto' }}
          priority
          className="object-contain"
        />
      </button>
    </div>
  );
};

export default ChatInput;
'use client';

import React, { useState, useEffect, useRef } from 'react';
import { addMessage, createUserMessage, createBotMessage, Message } from '@/app/utils/MessageManager';
import ReactMarkdown from 'react-markdown';
import remarkBreaks from 'remark-breaks';

export interface ChatBoxProps {
  title: string;
  askEndpoint: string;
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  className: string;
}

const ChatBox: React.FC<ChatBoxProps> = ({ askEndpoint, messages, setMessages, className }) => {
  const [input, setInput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const textareaContRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const wasNearBottomRef = useRef<boolean>(true);

  const sendTechnicalMessage = async (message: string) => {
    setMessages((prev) => [...prev, { sender: 'bot', text: message }]);
  };

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
    textareaResize();
    hitEnter();
  }, []);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [textareaRef, messages.length]);

  useEffect(() => {
    if (chatContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = chatContainerRef.current;
      wasNearBottomRef.current = scrollHeight - scrollTop - clientHeight < 100;
    }

    const raf = requestAnimationFrame(() => {
      if (wasNearBottomRef.current || messages[messages.length - 1]?.sender === 'user') {
        scrollToBottom();
      }
    });
    return () => cancelAnimationFrame(raf);
  }, [messages]);

  const scrollToBottom = () => {
    if (chatContainerRef.current) {
      console.log('Scrolling to bottom');
      chatContainerRef.current.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  };

  const hitEnter = () => {
    const sendBtn = document.querySelector('.sendBtn') as HTMLElement | null;
    document.querySelectorAll('.skgpt-input-textarea').forEach((input) => {
      input.addEventListener('keydown', (e: Event) => {
        if (e instanceof KeyboardEvent && e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          sendBtn?.click();
        }
      });
    });
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    setMessages((prev) => addMessage(prev, createUserMessage(input)));
    setInput('');
    setIsLoading(true);
    wasNearBottomRef.current = true; 

    if (textareaRef.current) {
      textareaRef.current.focus();
    }

    const threadId = localStorage.getItem('threadId');
    const chroma_conversation_id = localStorage.getItem('chroma_conversation_id');

    if (!threadId) {
      await sendTechnicalMessage('No thread ID found. Please wait for the thread to be created.');
      setIsLoading(false);
      return;
    }
    if (!chroma_conversation_id) {
      await sendTechnicalMessage('No chroma_conversation_id found. Please wait for the thread to be created.');
      setIsLoading(false);
      return;
    }

    try {
      setMessages((prev) => addMessage(prev, createBotMessage('')));

      const response = await fetch(askEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: input,
          thread_id: threadId,
          chroma_conversation_id,
        }),
      });

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No reader available');

      let fullMessage = '';
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += new TextDecoder().decode(value);
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const chunk = line.slice(6);
            fullMessage += chunk;

            setMessages((prev) => {
              const newMessages = [...prev];
              newMessages[newMessages.length - 1] = createBotMessage(fullMessage);
              return newMessages;
            });
          }
        }
      }
    } catch (error) {
      console.error(error);
      setMessages((prev) => addMessage(prev, createBotMessage('Error: Could not get a response.')));
    } finally {
      setIsLoading(false);
    }
  };

  const textareaResize = () => {
    const textarea = textareaRef.current;
    const textareaCont = textareaContRef.current;

    if (textarea && textareaCont) {
      const resize = () => {
        textareaCont.style.height = 'auto';
        textareaCont.style.height = `${Math.min(textarea.scrollHeight + 20, 200)}px`;
      };
      textarea.addEventListener('input', resize);
      resize();
      return () => textarea.removeEventListener('input', resize);
    }
  };

  //  For different fixed heights you should change these prop: h-[60vh] max-h-[60vh] 
  return (
    <div className={`flex flex-col h-full gap-4 justify-between ${className}`}>
      <div
        className="chatMessages flex flex-col gap-4 p-4 sm:p-6 md:p-8 overflow-y-auto scroll-smooth bg-white rounded-[20px] h-[60vh] max-h-[60vh]"
        ref={chatContainerRef}
      >
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`p-4 sm:p-5 md:p-6 rounded-[30px] max-w-[90%] sm:max-w-[80%] transition-opacity duration-300 ${
              msg.sender === 'user'
                ? 'bg-gradient-to-r from-[#1ea974] to-[#17a267] self-end text-white rounded-tl-[30px] rounded-br-[0]'
                : 'bg-[#ececec] self-start text-black rounded-tr-[30px] rounded-bl-[0] shadow-sm'
            }`}
          >
            {msg.sender === 'bot' ? (
              <div className="flex flex-col">
                <ReactMarkdown
                  remarkPlugins={[remarkBreaks]}
                  components={{
                    ol: ({ children }) => <ol className="pl-6 sm:pl-8 list-decimal">{children}</ol>,
                    ul: ({ children }) => <ul className="pl-6 sm:pl-8 list-disc">{children}</ul>,
                    p: ({ children }) => <p className="mb-2">{children}</p>,
                    h3: ({ children }) => (
                      <h3 className="text-lg sm:text-xl font-semibold mb-3 text-black">{children}</h3>
                    ),
                  }}
                >
                  {msg.text.replace(/\\n/g, '\n')}
                </ReactMarkdown>
              </div>
            ) : (
              <div className="text-sm sm:text-base">{msg.text}</div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="loading flex justify-center items-center p-4">
            <div className="animate-pulse flex space-x-2">
              <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
            </div>
          </div>
        )}
      </div>
      <div className="flex items-end gap-2 sm:gap-3 p-2 sm:p-4">
        <div
          className="flex flex-1 bg-gray-100 p-3 sm:p-4 rounded-[20px] transition-all duration-200 max-h-[150px] shadow-sm"
          ref={textareaContRef}
        >
          <textarea
            ref={textareaRef}
            rows={1}
            className="skgpt-input-textarea border-none text-sm sm:text-base text-black resize-none bg-transparent w-full font-[Poppins] min-h-[30px] placeholder:text-gray-500 focus:outline-none"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Write your question here..."
          />
        </div>
        <button
          className="skgpt-btn sendBtn h-10 sm:h-12 w-20 sm:w-24 text-base sm:text-lg text-white bg-[#1ea974] rounded-full border-none cursor-pointer hover:bg-[#17a267] transition-colors duration-200 disabled:opacity-50"
          onClick={sendMessage}
          disabled={isLoading || !input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatBox;
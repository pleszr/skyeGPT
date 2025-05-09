'use client';

import React, { useState, useEffect, useRef, useCallback, memo, useMemo } from 'react';
import Image from 'next/image';
import { addMessage, createUserMessage, createBotMessage, Message } from '@/app/utils/messageManager';
import ReactMarkdown from 'react-markdown';
import remarkBreaks from 'remark-breaks';
import { debounce } from 'lodash';
import remarkGfm from 'remark-gfm';

export interface ChatBoxProps {
  askEndpoint: string;
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  className?: string;
}

const MAX_RETRIES = 2;
const INITIAL_TEXTAREA_CONTENT_HEIGHT_PX_STR = '98px';
const MAX_TEXTAREA_HEIGHT_PX = 98;

const getChunkTextFromSSE = (chunk: string | number | boolean | { text?: unknown; message?: string; content?: string; response?: string; } | null | undefined): string =>  {
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


const ChatBox: React.FC<ChatBoxProps> = ({ askEndpoint, messages, setMessages, className }) => {
  const [input, setInput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isFeedbackModalOpen, setIsFeedbackModalOpen] = useState<boolean>(false);
  const [isConfirmationModalOpen, setIsConfirmationModalOpen] = useState<boolean>(false);
  const [feedbackText, setFeedbackText] = useState<string>('');
  const [feedbackError, setFeedbackError] = useState<string>('');
  const [submitError, setSubmitError] = useState<string>('');
  const [ratingError, setRatingError] = useState<{ [key: number]: string }>({});
  const [feedbackState, setFeedbackState] = useState<{ [key: number]: 'thumbs-up' | 'thumbs-down' | null }>({});
  const [activeMessageIndex, setActiveMessageIndex] = useState<number | null>(null);

  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const wasNearBottomRef = useRef<boolean>(true);
  const streamAbortControllerRef = useRef<AbortController | null>(null);

  const submitFeedbackEndpoint = process.env.NEXT_PUBLIC_SKYEGPT_SUBMIT_FEEDBACK_ENDPOINT || '/mock/api/submitFeedback';
  const submitRatingEndpoint = process.env.NEXT_PUBLIC_SKYEGPT_SUBMIT_RATING_ENDPOINT || '/mock/api/submitRating';

  const debouncedScrollToBottom = useMemo(() => debounce(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, 100), []);

  const scrollToBottom = useCallback(() => {
    if (wasNearBottomRef.current) {
        debouncedScrollToBottom();
    }
  }, [debouncedScrollToBottom]);

  const sendTechnicalMessage = useCallback(async (messageText: string) => {
    setMessages((prev) => [...prev, createBotMessage(messageText)]);
  }, [setMessages]);

  const textareaResize = useCallback(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      const newScrollHeight = textarea.scrollHeight;
      textarea.style.height = `${Math.min(newScrollHeight, MAX_TEXTAREA_HEIGHT_PX)}px`;
    }
  }, []);

  const sendMessage = useCallback(async () => {
    const trimmedInput = input.trim();
    if (!trimmedInput || isLoading) return;

    if (streamAbortControllerRef.current) {
        streamAbortControllerRef.current.abort();
    }
    streamAbortControllerRef.current = new AbortController();

    setMessages((prev) => addMessage(prev, createUserMessage(trimmedInput)));
    setInput('');
    if (textareaRef.current) {
        textareaRef.current.value = '';
        textareaResize();
    }
    setIsLoading(true);
    wasNearBottomRef.current = true;

    const conversationId = localStorage.getItem('chroma_conversation_id');

    if (!conversationId) {
      await sendTechnicalMessage('Error: Conversation ID not found. Please refresh or try again.');
      setIsLoading(false);
      return;
    }

    const hiddenInstruction = "Output raw GitHub Flavored Markdown (GFM). Do not wrap the entire response in ```markdown``` fences. Single newlines will be rendered as hard line breaks. Use standard GFM for all elements (headings, lists, paragraphs, etc.), as styling is handled automatically. Do not embed any HTML tags or custom CSS. Use `\n` for newlines.";
    const queryToSendToBackend = `${hiddenInstruction}\n\nUser query: ${trimmedInput}`;

    let fullMessageTextForCurrentResponse = '';

    const fetchStream = async (attempt: number): Promise<boolean> => {
      try {
        if (attempt === 0) {
            fullMessageTextForCurrentResponse = '';
            setMessages((prev) => addMessage(prev, createBotMessage('')));
        } else {
            setMessages((prev) => {
                const newMessages = [...prev];
                const lastMessage = newMessages[newMessages.length - 1];
                if(lastMessage && lastMessage.sender === 'bot') {
                    newMessages[newMessages.length - 1] = createBotMessage('');
                    fullMessageTextForCurrentResponse = '';
                }
                return newMessages;
            });
        }

        const response = await fetch(askEndpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream',
          },
          body: JSON.stringify({
            conversation_id: conversationId,
            query: queryToSendToBackend,
          }),
          signal: streamAbortControllerRef.current?.signal,
        });

        if (!response.ok) {
          throw new Error(`Server error: ${response.status} ${response.statusText}`);
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error('Failed to get stream reader.');

        let buffer = '';

        while (true) {
          if (streamAbortControllerRef.current?.signal.aborted) {
            reader.cancel();
            throw new Error("Stream aborted");
          }
          const { value, done } = await reader.read();
          if (done) {
            if (!fullMessageTextForCurrentResponse.trim()) {
              setMessages((prev) => {
                const newMessages = [...prev];
                const lastMessage = newMessages[newMessages.length - 1];
                if (lastMessage?.sender === 'bot') {
                  newMessages[newMessages.length - 1] = createBotMessage(
                    `No response received from the server${attempt < MAX_RETRIES ? '. Retrying...' : '. Please try again.'}`
                  );
                  fullMessageTextForCurrentResponse = lastMessage.text;
                }
                return newMessages;
              });
              return false;
            }
            setMessages((prevMsgs) => {
                const newMsgs = [...prevMsgs];
                const lastMsg = newMsgs[newMsgs.length - 1];
                if (lastMsg && lastMsg.sender === 'bot' && lastMsg.text !== fullMessageTextForCurrentResponse) {
                    newMsgs[newMsgs.length - 1] = createBotMessage(fullMessageTextForCurrentResponse);
                }
                return newMsgs;
            });
            return true;
          }

          buffer += new TextDecoder().decode(value);
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (streamAbortControllerRef.current?.signal.aborted) break;
            if (line.startsWith('data: ')) {
              try {
                const dataStr = line.slice(6);
                let parsedChunk;
                try {
                  parsedChunk = JSON.parse(dataStr);
                } catch {
                  parsedChunk = dataStr.trim() ? { text: dataStr } : null;
                }
                const chunkText = getChunkTextFromSSE(parsedChunk);
                if (chunkText) {
                  fullMessageTextForCurrentResponse += chunkText;
                  setMessages((prevMsgs) => {
                      const newMsgs = [...prevMsgs];
                      const lastMsg = newMsgs[newMsgs.length - 1];
                      if (lastMsg && lastMsg.sender === 'bot') {
                          newMsgs[newMsgs.length - 1] = createBotMessage(fullMessageTextForCurrentResponse);
                      }
                      return newMsgs;
                  });
                }
              } catch (e) {
                console.warn('Invalid SSE chunk processing error:', e, 'Original line:', line);
              }
            }
          }
            if (streamAbortControllerRef.current?.signal.aborted) break;
        }
        return true;
      } catch (error: unknown)  {
        if (
          typeof error === 'object' &&
          error !== null &&
          ('name' in error || 'message' in error)
        ) {
          const errObj = error as { name?: string; message?: string };
          if (errObj.name === 'AbortError' || errObj.message === "Stream aborted") {
            console.log("Fetch aborted by new request.");
            return true;
          }
        }
        console.error(`Send message error (attempt ${attempt + 1}/${MAX_RETRIES + 1}):`, error);
        setMessages((prev) => {
          const newMessages = [...prev];
          const lastMessage = newMessages[newMessages.length - 1];
          if (lastMessage?.sender === 'bot') {
            newMessages[newMessages.length - 1] = createBotMessage(
                `Error: Could not get a response. ${error instanceof Error ? error.message : String(error)}${attempt < MAX_RETRIES ? '. Retrying...' : '. Please try again later.'}`
            );
            fullMessageTextForCurrentResponse = lastMessage.text;
          }
          return newMessages;
        });
        return false;
      }
    };

    let attempt = 0;
    let success = false;
    while (attempt <= MAX_RETRIES && !success) {
      if(streamAbortControllerRef.current?.signal.aborted) {
          console.log("Send message loop aborted.");
          break;
      }
      success = await fetchStream(attempt);
      if (!success && attempt < MAX_RETRIES && !streamAbortControllerRef.current?.signal.aborted) {
        await new Promise((resolve) => setTimeout(resolve, 1000 * (attempt + 1)));
      }
      attempt++;
    }

    setIsLoading(false);
  }, [input, isLoading, setMessages, sendTechnicalMessage, askEndpoint, textareaResize]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey && input.trim() && !isLoading) {
        e.preventDefault();
        sendMessage();
      }
    },
    [input, isLoading, sendMessage]
  );

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.focus();
      textarea.addEventListener('input', textareaResize);
      textarea.style.height = INITIAL_TEXTAREA_CONTENT_HEIGHT_PX_STR;
      textareaResize();
    }
    return () => {
      if (textarea) {
        textarea.removeEventListener('input', textareaResize);
      }
      if(streamAbortControllerRef.current){
          streamAbortControllerRef.current.abort();
      }
    };
  }, [textareaResize]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);


  const debouncedHandleRating = useMemo(
    () =>
      debounce(async (messageIndex: number, rating: 'thumbs-up' | 'thumbs-down') => {
        const currentRating = feedbackState[messageIndex];
        const newRating = currentRating === rating ? null : rating;
        const previousRatingState = feedbackState[messageIndex];

        setFeedbackState((prev) => ({ ...prev, [messageIndex]: newRating }));
        setRatingError((prev) => ({ ...prev, [messageIndex]: '' }));

        const conversationId = localStorage.getItem('chroma_conversation_id');
        if (!conversationId) {
            console.error("Cannot submit rating: chroma_conversation_id is missing.");
            setRatingError((prev) => ({ ...prev, [messageIndex]: 'Session ID missing. Cannot submit rating.' }));
            setFeedbackState((prev) => ({ ...prev, [messageIndex]: previousRatingState }));
            return;
        }
        if (newRating === null) {
            return;
        }

        try {
          const response = await fetch(submitRatingEndpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              message_index: messageIndex,
              rating: newRating,
              chroma_conversation_id: conversationId,
            }),
          });

          if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(`Server error: ${response.status} - ${errorData.message || response.statusText}`);
          }
        } catch (error) {
          console.error('Error submitting rating:', error);
          setFeedbackState((prev) => ({ ...prev, [messageIndex]: previousRatingState }));
          const errorMessage =
            error instanceof Error && error.message.includes('Failed to fetch')
              ? 'Failed to connect to the server.'
              : (error instanceof Error ? error.message : 'Error submitting rating.');
          setRatingError((prev) => ({ ...prev, [messageIndex]: errorMessage }));
        }
      }, 300),
    [submitRatingEndpoint, feedbackState]
  );

  const handleFeedbackPromptClick = useCallback((messageIndex: number) => {
    setActiveMessageIndex(messageIndex);
    setFeedbackText('');
    setFeedbackError('');
    setSubmitError('');
    setIsFeedbackModalOpen(true);
  }, []);

  const handleFeedbackModalClose = useCallback(() => {
    setIsFeedbackModalOpen(false);
    setFeedbackText('');
    setFeedbackError('');
    setSubmitError('');
  }, []);

  const handleFeedbackSubmit = useCallback(async () => {
    if (activeMessageIndex === null || !feedbackText.trim()) {
      setFeedbackError('Feedback cannot be empty.');
      return;
    }
    setFeedbackError('');
    setSubmitError('');

    const conversationId = localStorage.getItem('chroma_conversation_id');
    if (!conversationId) {
        console.error("Cannot submit feedback: chroma_conversation_id is missing.");
        setSubmitError('Session ID missing. Cannot submit feedback.');
        return;
    }
    const rating = feedbackState[activeMessageIndex] || null;

    const tempSubmittedFeedbackText = feedbackText;

    try {
      const response = await fetch(submitFeedbackEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message_index: activeMessageIndex,
          feedback_text: tempSubmittedFeedbackText,
          rating,
          chroma_conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`Server error: ${response.status} - ${errorData.message || response.statusText}`);
      }

      setIsFeedbackModalOpen(false);
      setIsConfirmationModalOpen(true);
    } catch (error) {
      console.error('Error submitting feedback:', error);
      const errorMessage =
        error instanceof Error && error.message.includes('Failed to fetch')
          ? 'Failed to connect to the server.'
          : (error instanceof Error ? error.message : 'Error submitting feedback.');
      setSubmitError(errorMessage);
    }
  }, [activeMessageIndex, feedbackText, feedbackState, submitFeedbackEndpoint]);

  const handleConfirmationModalClose = useCallback(() => {
    setIsConfirmationModalOpen(false);
    setActiveMessageIndex(null);
    setFeedbackText('');
  }, []);

  const modalHeader = useMemo(() => {
    if (activeMessageIndex === null) return 'Share Your Feedback';
    return feedbackState[activeMessageIndex] === 'thumbs-down' ? 'Report an Issue' : 'Share Your Feedback';
  }, [activeMessageIndex, feedbackState]);

  const textareaPlaceholder = useMemo(() => {
    if (activeMessageIndex === null) return 'Write your feedback here...';
    return feedbackState[activeMessageIndex] === 'thumbs-down' ? 'Describe the issue or why this response is problematic...' : 'What did you like or what could be improved?';
  }, [activeMessageIndex, feedbackState]);

  const confirmationMessage = useMemo(() => {
    if (activeMessageIndex === null) return 'Feedback Sent!';
    return feedbackState[activeMessageIndex] === 'thumbs-down' ? 'Issue Report Sent!' : 'Feedback Sent!';
  }, [activeMessageIndex, feedbackState]);

  return (
    <div className={`flex flex-col h-full ${className || ''}`}>
      <div
        className="chatMessages flex flex-col gap-6 p-4 sm:p-6 md:p-8 overflow-y-auto scroll-smooth bg-white rounded-[20px] h-[60vh] max-h-[60vh] min-h-0"
        ref={chatContainerRef}
      >
        {messages.length === 0 && !isLoading && (
          <div className="h-full flex flex-col items-center justify-center text-center text-gray-400 text-sm p-4">
            <span>No messages yet.</span>
            <span>Start the conversation below!</span>
          </div>
        )}
        {messages.map((msg, index) => (
          <MemoizedMessage
            key={index}
            msg={msg}
            index={index}
            isLastBotMessage={msg.sender === 'bot' && index === messages.length -1 && !isLoading && !streamAbortControllerRef.current?.signal.aborted}
            feedbackType={feedbackState[index]}
            currentRatingError={ratingError[index]}
            onRate={(rating) => debouncedHandleRating(index, rating)}
            onPromptFeedback={() => handleFeedbackPromptClick(index)}
          />
        ))}
        {isLoading && messages.length > 0 && messages[messages.length -1]?.sender === 'user' && !messages[messages.length -1]?.text.includes("Error:") && !messages[messages.length -1]?.text.includes("No response received") && (
          <div className="self-start max-w-[90%] sm:max-w-[80%] flex flex-col">
            <div className="p-4 sm:p-5 md:p-6 rounded-[30px] bg-[#ececec] text-black rounded-tr-[30px] rounded-bl-[0] shadow-sm">
                <div className="animate-pulse flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                </div>
            </div>
          </div>
        )}
          {isLoading && messages.length === 0 && (
            <div className="h-full flex items-center justify-center">
                <div className="animate-pulse flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                </div>
            </div>
        )}
      </div>
      <div className="flex items-center p-2 sm:p-3 gap-2 sm:gap-3 border-t border-gray-200 bg-white shrink-0">
        <div
          className="flex-1 bg-gray-100 rounded-[20px] transition-all duration-200 shadow-sm flex items-end"
        >
          <textarea
            ref={textareaRef}
            rows={1}
            className="border-none text-sm sm:text-base text-black resize-none bg-transparent w-full py-2 px-3 font-[Poppins] placeholder:text-gray-500 focus:outline-none"
            style={{ minHeight: INITIAL_TEXTAREA_CONTENT_HEIGHT_PX_STR }}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            onPaste={textareaResize}
            onInput={textareaResize}
            placeholder="Write your question here..."
            disabled={isLoading}
          />
        </div>
        <button
          className="skgpt-btn sendBtn p-0 border-none bg-transparent cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center shrink-0 hover:opacity-80 transition-opacity"
          onClick={sendMessage}
          disabled={isLoading || !input.trim()}
          title="Send"
          aria-label="Send message"
        >
          <Image
            src="/button.png"
            alt="Send"
            width={120}
            height={120}
            quality={100}
            priority
            className="object-contain"
          />
        </button>
      </div>

      {isFeedbackModalOpen && activeMessageIndex !== null && (
        <div className="fixed inset-0 flex items-center justify-center bg-transparent backdrop-blur-md z-50 p-4">
          <div
            className="bg-white rounded-[20px] shadow-xl p-6 w-full max-w-lg flex flex-col gap-4"
            role="dialog"
            aria-labelledby="feedback-modal-header"
            aria-modal="true"
          >
            <div className="flex justify-between items-center">
              <h2 id="feedback-modal-header" className="text-lg font-semibold text-gray-800 flex-1 text-center">{modalHeader}</h2>
              <button
                onClick={handleFeedbackModalClose}
                className="text-gray-500 hover:text-gray-700 text-2xl leading-none"
                aria-label="Close feedback modal"
              >
                &times;
              </button>
            </div>
            <div className="flex flex-col gap-2 flex-1">
              <textarea
                className={`w-full min-h-[100px] p-3 rounded-[10px] bg-gray-100 text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#1ea974] resize-none border ${
                  feedbackError || submitError ? 'border-red-500 ring-red-500' : 'border-gray-300'
                }`}
                placeholder={textareaPlaceholder}
                value={feedbackText}
                onChange={(e) => {
                  setFeedbackText(e.target.value);
                  if (feedbackError) setFeedbackError('');
                  if (submitError) setSubmitError('');
                }}
                aria-invalid={!!feedbackError || !!submitError}
                aria-describedby={feedbackError ? 'feedback-input-error' : submitError ? 'feedback-submit-error' : undefined}
              />
              {feedbackError && (
                <p id="feedback-input-error" className="text-red-600 text-sm">
                  {feedbackError}
                </p>
              )}
              {submitError && (
                <p id="feedback-submit-error" className="text-red-600 text-sm">
                  {submitError}
                </p>
              )}
            </div>
            <div className="flex justify-center items-center">
              <button
                onClick={handleFeedbackSubmit}
                className={`px-8 py-3 rounded-full text-white font-semibold transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                  feedbackText.trim()
                    ? 'bg-[#1ea974] hover:bg-[#17a267] focus:ring-[#1ea974]'
                    : 'bg-gray-400 cursor-not-allowed'
                }`}
                disabled={!feedbackText.trim()}
                aria-label="Submit feedback"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}

      {isConfirmationModalOpen && (
        <div className="fixed inset-0 flex items-center justify-center bg-transparent backdrop-blur-md z-50 p-4">
          <div
            className="bg-white rounded-[20px] shadow-xl p-6 w-full max-w-md flex flex-col gap-4 items-center"
            role="alertdialog"
            aria-labelledby="confirmation-modal-header"
            aria-modal="true"
          >
            <div className="w-full flex justify-between items-center">
                <span className="w-6"></span>
                <h2 id="confirmation-modal-header" className="text-lg font-semibold text-gray-800 text-center flex-1">{confirmationMessage}</h2>
              <button
                  onClick={handleConfirmationModalClose}
                  className="text-gray-500 hover:text-gray-700 text-2xl leading-none"
                  aria-label="Close confirmation"
              >
                  &times;
              </button>
            </div>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-16 w-16 text-[#17a267]"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
              aria-hidden="true"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
            </svg>
            <p className="text-xl font-bold text-gray-800 text-center">{confirmationMessage}</p>
            <p className="text-center text-gray-600">Thank you for your input!</p>
            <button
                onClick={handleConfirmationModalClose}
                className="mt-2 px-6 py-2 rounded-full text-white bg-[#1ea974] hover:bg-[#17a267] transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-[#1ea974] focus:ring-offset-2"
                aria-label="Close confirmation"
            >
                Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

interface MemoizedMessageProps {
  msg: Message;
  index: number;
  isLastBotMessage: boolean;
  feedbackType: 'thumbs-up' | 'thumbs-down' | null;
  currentRatingError?: string;
  onRate: (rating: 'thumbs-up' | 'thumbs-down') => void;
  onPromptFeedback: () => void;
}

const MemoizedMessage = memo(
  ({ msg, index, isLastBotMessage, feedbackType, currentRatingError, onRate, onPromptFeedback }: MemoizedMessageProps) => {
    const isUser = msg.sender === 'user';

    return (
      <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
        {isUser ? (
          <div
            className={`p-4 sm:p-5 md:p-6 rounded-[30px] max-w-[90%] sm:max-w-[80%] transition-opacity duration-300 shadow-sm bg-gradient-to-r from-[#1ea974] to-[#17a267] self-end text-white rounded-br-[0]`}
          >
            <div className="text-sm sm:text-base whitespace-pre-wrap break-words">{msg.text}</div>
          </div>
        ) : (
          <div className="self-start flex flex-col w-auto max-w-[90%] sm:max-w-[80%]">
            <div
              className={`p-4 sm:p-5 md:p-6 rounded-[30px] transition-opacity duration-300 shadow-sm bg-[#ececec] text-black rounded-bl-[0]`}
            >
              <div className="prose prose-sm sm:prose-base max-w-none text-black break-words">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm, remarkBreaks]}
                  components={{
                    ol: ({ children }) => <ol className="pl-6 sm:pl-8 list-decimal">{children}</ol>,
                    ul: ({ children }) => <ul className="pl-6 sm:pl-8 list-disc">{children}</ul>,
                    p: ({ children }) => <p className="mb-2">{children}</p>,
                    h1: ({ children }) => (
                      <h1 className="text-2xl sm:text-3xl font-bold mb-3 text-black">{children}</h1>
                    ),
                    h2: ({ children }) => (
                      <h2 className="text-xl sm:text-2xl font-semibold mb-3 text-black">{children}</h2>
                    ),
                    h3: ({ children }) => (
                      <h3 className="text-lg sm:text-xl font-semibold mb-3 text-black">{children}</h3>
                    ),
                    h4: ({ children }) => (
                      <h4 className="text-base sm:text-lg font-semibold mb-3 text-black">{children}</h4>
                    ),
                    h5: ({ children }) => (
                      <h5 className="text-sm sm:text-base font-semibold mb-3 text-black">{children}</h5>
                    ),
                    h6: ({ children }) => (
                      <h6 className="text-xs sm:text-sm font-semibold mb-3 text-black">{children}</h6>
                    ),
                  }}
                >
                  {msg.text.replace(/\\n/g, '\n')}
                </ReactMarkdown>
              </div>
            </div>

            {isLastBotMessage && msg.text.trim() !== '' && (
              <div className="flex items-center gap-2 justify-end mt-2">
                <button
                  onClick={onPromptFeedback}
                  className="text-xs text-gray-600 hover:text-gray-900 hover:underline transition-colors duration-200"
                  title="Provide detailed feedback"
                  aria-label="Provide detailed feedback for this message"
                >
                  GIVE FEEDBACK
                </button>
                {(['thumbs-up', 'thumbs-down'] as const).map((ratingType) => (
                  <button
                    key={ratingType}
                    onClick={() => onRate(ratingType)}
                    className={`transition-all duration-200 transform hover:scale-125 rounded-full ${feedbackType === ratingType ? 'opacity-100' : 'opacity-60 hover:opacity-90'} ${feedbackType === ratingType && ratingType === 'thumbs-up' ? 'bg-green-100' : ''} ${feedbackType === ratingType && ratingType === 'thumbs-down' ? 'bg-red-100' : ''}`}
                    title={ratingType === 'thumbs-up' ? "Helpful" : "Not helpful"}
                    aria-label={ratingType === 'thumbs-up' ? "Mark as helpful" : "Mark as not helpful"}
                    aria-pressed={feedbackType === ratingType}
                    aria-describedby={currentRatingError ? `rating-error-${index}` : undefined}
                  >
                    <Image
                      src={ratingType === 'thumbs-up' ? "/tup.png" : "/tdown.png"}
                      alt={ratingType === 'thumbs-up' ? "Thumbs Up" : "Thumbs Down"}
                      width={16}
                      height={16}
                      className={`object-contain ${feedbackType === ratingType && ratingType === 'thumbs-up' ? 'skgpt-tint-green-active' : ''} ${feedbackType === ratingType && ratingType === 'thumbs-down' ? 'skgpt-tint-red-active' : ''}`}
                    />
                  </button>
                ))}
              </div>
            )}

            {isLastBotMessage && currentRatingError && (
              <div className="flex justify-end mt-1 w-full">
                <p id={`rating-error-${index}`} className="text-red-500 text-xs" aria-live="polite">
                  {currentRatingError}
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    );
  },
  (prevProps, nextProps) => {
    return (
      prevProps.msg.text === nextProps.msg.text &&
      prevProps.msg.sender === nextProps.msg.sender &&
      prevProps.index === nextProps.index &&
      prevProps.isLastBotMessage === nextProps.isLastBotMessage &&
      prevProps.feedbackType === nextProps.feedbackType &&
      prevProps.currentRatingError === nextProps.currentRatingError
    );
  }
);

MemoizedMessage.displayName = 'MemoizedMessage';

export default memo(ChatBox);
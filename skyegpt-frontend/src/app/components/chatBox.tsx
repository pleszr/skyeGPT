'use client';

import React, { useState, useEffect, useRef, useCallback, memo, useMemo } from 'react';
import Image from 'next/image';
import { addMessage, createUserMessage, createBotMessage, Message } from '@/app/utils/messageManager';
import ReactMarkdown from 'react-markdown';
import remarkBreaks from 'remark-breaks';
import { debounce } from 'lodash';
import remarkGfm from 'remark-gfm';


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
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isConfirmationModalOpen, setIsConfirmationModalOpen] = useState<boolean>(false);
  const [feedbackText, setFeedbackText] = useState<string>('');
  const [feedbackError, setFeedbackError] = useState<string>('');
  const [submitError, setSubmitError] = useState<string>('');
  const [ratingError, setRatingError] = useState<{ [key: number]: string }>({});
  const [feedbackState, setFeedbackState] = useState<{ [key: number]: 'thumbs-up' | 'thumbs-down' | null }>({});
  const [activeMessageIndex, setActiveMessageIndex] = useState<number | null>(null);
  const maxRetries = 2;
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const textareaContRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const wasNearBottomRef = useRef<boolean>(true);

  const submitFeedbackEndpoint = process.env.NEXT_PUBLIC_SKYEGPT_SUBMIT_FEEDBACK_ENDPOINT || '/mock/api/submitFeedback';
  const submitRatingEndpoint = process.env.NEXT_PUBLIC_SKYEGPT_SUBMIT_RATING_ENDPOINT || '/mock/api/submitRating';

  const debouncedScrollToBottom = debounce(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, 100);

  const scrollToBottom = useCallback(() => {
    debouncedScrollToBottom();
  }, [debouncedScrollToBottom]);

  const sendTechnicalMessage = useCallback(async (message: string) => {
    setMessages((prev) => [...prev, { sender: 'bot', text: message }]);
  }, [setMessages]);

  const textareaResize = useCallback(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = '50px';
      const newHeight = Math.min(textarea.scrollHeight, 98);
      textarea.style.height = `${newHeight}px`;
    }
  }, []);

  const sendMessage = useCallback(async () => {
    const trimmedInput = input.trim();
    if (!trimmedInput) return;

    setMessages((prev) => addMessage(prev, createUserMessage(trimmedInput)));
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = '50px';
    }
    setIsLoading(true);
    wasNearBottomRef.current = true;

    const conversationId = localStorage.getItem('chroma_conversation_id');

    if (!conversationId) {
      await sendTechnicalMessage('No conversation ID found. Please wait for the conversation to be created.');
      setIsLoading(false);
      return;
    }

    // Hidden instruction BY DEFAULT - OUR AI DOES NOT SENDING THE RESPONSE IN MARKDOWN FORMAT, In order to format the response - WE NEED TO ADD A HIDDEN INSTRUCTION
    const hiddenInstruction = "Please provide your full response as a GitHub Flavored Markdown document, only contents , dont wrap the entire thing in a '''markdown''' code"
    const queryToSendToBackend = `${hiddenInstruction}\n\nUser query: ${trimmedInput}`;
    
    // If we fixed this in the BACKEND - we can go back the non-hidden instructions (WE JUST NEED TO ADD NEW INSTRUCTIONS))
    //const queryToSendToBackend = `\n\nUser query: ${trimmedInput}`; // Using direct query

    const fetchStream = async (attempt: number): Promise<boolean> => {
      try {
        setMessages((prev) => addMessage(prev, createBotMessage('')));

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
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch streaming response: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error('No reader available');

        let fullMessage = '';
        let buffer = '';

        while (true) {
          const { value, done } = await reader.read();
          if (done) {
            if (!fullMessage.trim()) {
              setMessages((prev) => {
                const newMessages = [...prev];
                if (newMessages.length > 0 && newMessages[newMessages.length - 1].sender === 'bot') {
                  newMessages[newMessages.length - 1] = createBotMessage(
                    `No response received from the server${attempt < maxRetries ? '. Retrying...' : '.'}`
                  );
                }
                return newMessages;
              });
              return false;
            }
            setMessages((prev) => {
              const newMessages = [...prev];
              if (newMessages.length > 0 && newMessages[newMessages.length - 1].sender === 'bot') {
                newMessages[newMessages.length - 1] = createBotMessage(fullMessage);
              }
              return newMessages;
            });
            break;
          }

          buffer += new TextDecoder().decode(value);
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const dataStr = line.slice(6);
                let chunk;
                try {
                  chunk = JSON.parse(dataStr);
                } catch {
                  chunk = { text: dataStr };
                }

                let derivedChunkText = '';
                if (chunk !== null && chunk !== undefined) {
                    if (typeof chunk === 'string') {
                        derivedChunkText = chunk;
                    } else if (chunk.text !== undefined && typeof chunk.text === 'string') {
                        derivedChunkText = chunk.text;
                    } else if (chunk.message !== undefined && typeof chunk.message === 'string') {
                        derivedChunkText = chunk.message;
                    } else if (chunk.content !== undefined && typeof chunk.content === 'string') {
                        derivedChunkText = chunk.content;
                    } else if (chunk.response !== undefined && typeof chunk.response === 'string') {
                        derivedChunkText = chunk.response;
                    } else if (typeof chunk === 'number' || typeof chunk === 'boolean') {
                        derivedChunkText = String(chunk);
                    }
                }
                const chunkText = derivedChunkText;



                const shouldFilter = false;
 

                if (shouldFilter) {
                  continue;
                }

                if (chunkText) {
                  fullMessage += chunkText;
                  setMessages((prev) => {
                    const newMessages = [...prev];
                    if (newMessages.length > 0 && newMessages[newMessages.length - 1].sender === 'bot') {
                      newMessages[newMessages.length - 1] = createBotMessage(fullMessage);
                    }
                    return newMessages;
                  });
                }

              } catch (e) {
                console.warn('Invalid SSE chunk processing error:', e, 'Original line:', line);
              }
            }
          }
        }
        return true;
      } catch (error) {
        console.error(`Send message error (attempt ${attempt + 1}):`, error);
        setMessages((prev) => {
          const newMessages = [...prev];
          if (newMessages.length > 0 && newMessages[newMessages.length - 1].sender === 'bot') {
            newMessages[newMessages.length - 1] = createBotMessage(
              `Error: Could not get a response${attempt < maxRetries ? '. Retrying...' : '.'}`
            );
          }
          return newMessages;
        });
        return false;
      }
    };

    let attempt = 0;
    let success = false;
    while (attempt <= maxRetries && !success) {
      success = await fetchStream(attempt);
      if (!success && attempt < maxRetries) {
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
      attempt++;
    }

    setIsLoading(false);
  }, [input, setMessages, sendTechnicalMessage, askEndpoint]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey && input.trim()) {
        e.preventDefault();
        sendMessage();
      }
    },
    [input, sendMessage]
  );

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.focus();
      textarea.addEventListener('input', textareaResize);
    }
    return () => {
      if (textarea) {
        textarea.removeEventListener('input', textareaResize);
      }
    };
  }, [textareaResize]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const debouncedHandleFeedback = useMemo(
    () =>
      debounce(async (messageIndex: number, feedback: 'thumbs-up' | 'thumbs-down') => {
        const currentFeedback = feedbackState[messageIndex];

        if (currentFeedback === feedback) {
          setFeedbackState((prev) => ({
            ...prev,
            [messageIndex]: null,
          }));
          setRatingError((prev) => ({ ...prev, [messageIndex]: '' }));
          return;
        }

        const previousFeedback = currentFeedback;
        setFeedbackState((prev) => ({
          ...prev,
          [messageIndex]: feedback,
        }));
        setRatingError((prev) => ({ ...prev, [messageIndex]: '' }));

        const conversationId = localStorage.getItem('chroma_conversation_id');
        if (!conversationId) {
            console.error("Cannot submit rating: chroma_conversation_id is missing.");
            setRatingError((prev) => ({ ...prev, [messageIndex]: 'Session ID missing.' }));
            setFeedbackState((prev) => ({ ...prev, [messageIndex]: previousFeedback }));
            return;
        }

        try {
          const response = await fetch(submitRatingEndpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              message_index: messageIndex,
              rating: feedback,
              chroma_conversation_id: conversationId,
            }),
          });

          if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
          }
        } catch (error) {
          console.error('Error submitting rating:', error);
          setFeedbackState((prev) => ({
            ...prev,
            [messageIndex]: previousFeedback,
          }));
          const errorMessage =
            error instanceof Error && error.message.includes('Failed to fetch')
              ? 'Failed to connect to the server.'
              : 'Error submitting rating.';
          setRatingError((prev) => ({ ...prev, [messageIndex]: errorMessage }));
        }
      }, 300),
    [submitRatingEndpoint, feedbackState]
  );

  const handleFeedbackPromptClick = useCallback((messageIndex: number) => {
    setActiveMessageIndex(messageIndex);
    setFeedbackError('');
    setSubmitError('');
    setIsModalOpen(true);
  }, []);

  const handleModalClose = useCallback(() => {
    setIsModalOpen(false);
    setFeedbackText('');
    setFeedbackError('');
    setSubmitError('');
  }, []);

  const handleFeedbackSubmit = useCallback(async () => {
    if (activeMessageIndex === null) return;

    if (!feedbackText.trim()) {
      setFeedbackError('Feedback cannot be empty.');
      return;
    }

    setSubmitError('');
    const conversationId = localStorage.getItem('chroma_conversation_id');
    if (!conversationId) {
        console.error("Cannot submit feedback: chroma_conversation_id is missing.");
        setSubmitError('Session ID missing.');
        return;
    }
    const rating = feedbackState[activeMessageIndex] || null;

    const tempFeedbackText = feedbackText;
    setFeedbackText(''); 

    try {
      const response = await fetch(submitFeedbackEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message_index: activeMessageIndex,
          feedback_text: tempFeedbackText,
          rating,
          chroma_conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      setIsConfirmationModalOpen(true);
    } catch (error) {
      console.error('Error submitting feedback:', error);
      setFeedbackText(tempFeedbackText); 
      const errorMessage =
        error instanceof Error && error.message.includes('Failed to fetch')
          ? 'Failed to connect to the server.'
          : 'Error submitting feedback.';
      setSubmitError(errorMessage);
    }
  }, [activeMessageIndex, feedbackText, feedbackState, submitFeedbackEndpoint]);

  const handleConfirmationModalClose = useCallback(() => {
    setIsConfirmationModalOpen(false);
    setIsModalOpen(false); 
    setActiveMessageIndex(null);
  }, []);

  const getModalHeader = useCallback(() => {
    if (activeMessageIndex === null) return 'Share your feedback';
    const feedbackVal = feedbackState[activeMessageIndex];
    return feedbackVal === 'thumbs-down' ? 'Report an Issue' : 'Share your feedback';
  }, [activeMessageIndex, feedbackState]);

  const getTextareaPlaceholder = useCallback(() => {
    if (activeMessageIndex === null) return 'write your feedback here...';
    const feedbackVal = feedbackState[activeMessageIndex];
    return feedbackVal === 'thumbs-down' ? 'write your issue here...' : 'write your feedback here...';
  }, [activeMessageIndex, feedbackState]);

  const getConfirmationMessage = useCallback(() => {
    if (activeMessageIndex === null) return 'Feedback Sent!';
    const feedbackVal = feedbackState[activeMessageIndex];
    return feedbackVal === 'thumbs-down' ? 'Report Sent!' : 'Feedback Sent!';
  }, [activeMessageIndex, feedbackState]);

  return (
    <div className={`flex flex-col gap-4 justify-between ${className}`}>
      <div
        className="chatMessages flex flex-col gap-6 p-4 sm:p-6 md:p-8 overflow-y-auto scroll-smooth bg-white rounded-[20px] h-[60vh] max-h-[60vh]"
        ref={chatContainerRef}
      >
        {messages.map((msg, index) => (
          <MemoizedMessage
            key={index}
            msg={msg}
            index={index}
            isLoading={isLoading}
            feedbackState={feedbackState}
            ratingError={ratingError}
            handleFeedback={debouncedHandleFeedback}
            handleFeedbackPromptClick={handleFeedbackPromptClick}
            messages={messages}
          />
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
      <div className="flex items-center p-2 sm:p-4 gap-6">
        <div
          className="flex-1 bg-gray-100 p-3 sm:p-2 rounded-[20px] transition-all duration-200 shadow-sm"
          ref={textareaContRef}
        >
          <textarea
            ref={textareaRef}
            rows={1}
            className="skgpt-input-textarea border-none text-sm sm:text-base text-black resize-none bg-transparent w-full h-[50px] font-[Poppins] placeholder:text-gray-500 focus:outline-none"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            onPaste={textareaResize}
            placeholder="Write your question here..."
          />
        </div>
        <button
          ref={buttonRef}
          className="skgpt-btn sendBtn border-none cursor-pointer disabled:opacity-50"
          onClick={sendMessage}
          disabled={isLoading || !input.trim()}
          title="Send"
        >
          <Image
            src="/button.png"
            alt="Send Button"
            width={120}
            height={120}
            quality={80}
            style={{ height: 'auto', width: 'auto' }}
            priority
            className="object-contain"
          />
        </button>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 flex items-center justify-center backdrop-blur-md z-50">
          <div
            className="bg-white rounded-[20px] shadow-lg p-6 w-[836px] h-[257.32px] max-w-[90vw] max-h-[80vh] flex flex-col gap-4
              xs:w-[95vw] xs:h-[200px]"
          >
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-semibold text-center flex-1">{getModalHeader()}</h2>
              <button
                onClick={handleModalClose}
                className="text-gray-600 hover:text-gray-800 text-xl"
                aria-label="Close Modal"
              >
                ✕
              </button>
            </div>
            <div className="flex flex-col gap-2 flex-1">
              <textarea
                className={`w-full h-full p-3 rounded-[10px] bg-gray-100 text-gray-800 placeholder-gray-500 focus:outline-none resize-none ${
                  feedbackError || submitError ? 'border-2 border-red-500' : ''
                }`}
                placeholder={getTextareaPlaceholder()}
                value={feedbackText}
                onChange={(e) => {
                  setFeedbackText(e.target.value);
                  setFeedbackError('');
                  setSubmitError('');
                }}
                aria-invalid={feedbackError || submitError ? 'true' : 'false'}
                aria-describedby={
                  feedbackError ? 'feedback-error' : submitError ? 'submit-error' : undefined
                }
              />
              {feedbackError && (
                <p id="feedback-error" className="text-red-500 text-sm">
                  {feedbackError}
                </p>
              )}
              {submitError && (
                <p id="submit-error" className="text-red-500 text-sm">
                  {submitError}
                </p>
              )}
            </div>
            <div className="flex justify-center items-center">
              <button
                onClick={handleFeedbackSubmit}
                className={`px-6 py-2 rounded-full text-white transition-colors duration-200 ${
                  feedbackText.trim()
                    ? 'bg-[#1ea974] hover:bg-[#17a267]'
                    : 'bg-gray-400 cursor-not-allowed'
                }`}
                disabled={!feedbackText.trim()}
                aria-label="Send Feedback"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}

      {isConfirmationModalOpen && (
        <div className="fixed inset-0 flex items-center justify-center backdrop-blur-md z-50">
          <div
            className="bg-white rounded-[20px] shadow-lg p-6 w-[436px] h-[257.32px] max-w-[90vw] max-h-[80vh] flex flex-col gap-4
              xs:w-[95vw] xs:h-[200px]"
          >
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-semibold text-center flex-1">{getModalHeader()}</h2>
              <button
                onClick={handleConfirmationModalClose}
                className="text-gray-600 hover:text-gray-800 text-xl"
                aria-label="Close Modal"
              >
                ✕
              </button>
            </div>
            <div className="flex flex-col items-center gap-2 flex-1 justify-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-12 w-12 text-[#17a267]"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
              <p className="text-lg font-bold text-center">{getConfirmationMessage()}</p>
              <p className="text-center text-gray-600">Thanks</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const MemoizedMessage = memo(
  ({
    msg,
    index,
    isLoading,
    feedbackState,
    ratingError,
    handleFeedback,
    handleFeedbackPromptClick,
    messages,
  }: {
    msg: Message;
    index: number;
    isLoading: boolean;
    feedbackState: { [key: number]: 'thumbs-up' | 'thumbs-down' | null };
    ratingError: { [key: number]: string };
    handleFeedback: (messageIndex: number, feedback: 'thumbs-up' | 'thumbs-down') => void;
    handleFeedbackPromptClick: (messageIndex: number) => void;
    messages: Message[];
  }) => {
    return (
      <div className="flex flex-col">
        {msg.sender === 'user' ? (
          <div
            className={`p-4 sm:p-5 md:p-6 rounded-[30px] max-w-[90%] sm:max-w-[80%] transition-opacity duration-300 bg-gradient-to-r from-[#1ea974] to-[#17a267] self-end text-white rounded-tl-[30px] rounded-br-[0]`}
          >
            <div className="text-sm sm:text-base">{msg.text}</div>
          </div>
        ) : (
          <div className="self-start max-w-[90%] sm:max-w-[80%] flex flex-col">
            <div
              className={`p-4 sm:p-5 md:p-6 rounded-[30px] transition-opacity duration-300 bg-[#ececec] text-black rounded-tr-[30px] rounded-bl-[0] shadow-sm`}
            >
              <div className="flex flex-col">
              <ReactMarkdown
                  remarkPlugins={[remarkBreaks, remarkGfm]}
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
            {msg.sender === 'bot' && (index !== messages.length - 1 || !isLoading) && msg.text.trim() !== '' && ( // Added check for non-empty bot message
              <div className="flex flex-col items-end gap-2 mt-2">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleFeedbackPromptClick(index)}
                    className="text-xs text-gray-600 hover:text-gray-800 transition-colors duration-200"
                    title="Give Feedback"
                  >
                    GIVE FEEDBACK
                  </button>
                  <button
                    onClick={() => handleFeedback(index, 'thumbs-up')}
                    className={`transition-all duration-200 transform hover:scale-125 hover:opacity-100 ${
                      feedbackState[index] === 'thumbs-up' ? 'opacity-100 tint-green' : 'opacity-60'
                    }`}
                    title="Thumbs Up"
                    aria-label="Thumbs Up"
                    aria-describedby={ratingError[index] ? `rating-error-${index}` : undefined}
                  >
                    <Image
                      src="/tup.png"
                      alt="Thumbs Up"
                      width={16} 
                      height={16}
                      // style={{ height: 'auto', width: 'auto' }}
                      priority={false}
                      className={`w-[16px] h-auto ${feedbackState[index] === 'thumbs-up' ? 'tint-green' : ''}`}
                    />
                  </button>
                  <button
                    onClick={() => handleFeedback(index, 'thumbs-down')}
                    className={`transition-all duration-200 transform hover:scale-125 hover:opacity-100 ${
                      feedbackState[index] === 'thumbs-down' ? 'opacity-100 tint-green' : 'opacity-60'
                    }`}
                    title="Thumbs Down"
                    aria-label="Thumbs Down"
                    aria-describedby={ratingError[index] ? `rating-error-${index}` : undefined}
                  >
                    <Image
                      src="/tdown.png"
                      alt="Thumbs Down"
                      width={16}
                      height={16} 
                      // style={{ height: 'auto', width: 'auto' }}
                      priority={false}
                      className={`w-[16px] h-auto ${feedbackState[index] === 'thumbs-down' ? 'tint-green' : ''}`}
                    />
                  </button>
                </div>
                {ratingError[index] && (
                  <p
                    id={`rating-error-${index}`}
                    className="text-red-500 text-xs mt-1"
                    aria-live="polite"
                  >
                    {ratingError[index]}
                  </p>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    );
  },
  (prevProps, nextProps) => {
    if (prevProps.msg.text !== nextProps.msg.text ||
        prevProps.msg.sender !== nextProps.msg.sender ||
        prevProps.index !== nextProps.index ||
        prevProps.isLoading !== nextProps.isLoading ||
        prevProps.feedbackState[prevProps.index] !== nextProps.feedbackState[nextProps.index] ||
        prevProps.ratingError[prevProps.index] !== nextProps.ratingError[nextProps.index] ||
        prevProps.messages.length !== nextProps.messages.length) {
      return false; 
    }
    return true;
  }
);

MemoizedMessage.displayName = 'MemoizedMessage';

export default memo(ChatBox);
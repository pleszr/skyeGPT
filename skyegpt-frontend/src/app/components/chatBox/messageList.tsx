'use client';

import React, { memo, useLayoutEffect, useCallback, useMemo } from 'react';
import Image from 'next/image';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { debounce } from 'lodash';
import { Message } from '@/app/utils/messageManager';
import { useLoadingAnimation } from '../../hooks/useLoadingAnimation';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
  dynamicLoadingTexts: string[];
  feedbackState: { [key: number]: 'thumbs-up' | 'thumbs-down' | null };
  ratingError: { [key: number]: string };
  onRate: (messageIndex: number, rating: 'thumbs-up' | 'thumbs-down') => void;
  onPromptFeedback: (messageIndex: number) => void;
  chatContainerRef: React.RefObject<HTMLDivElement>;
}

const MessageList: React.FC<MessageListProps> = ({
  messages,
  isLoading,
  dynamicLoadingTexts,
  feedbackState,
  ratingError,
  onRate,
  onPromptFeedback,
  chatContainerRef
}) => {
  const { animatedLoadingElements } = useLoadingAnimation(isLoading, dynamicLoadingTexts);

  const debouncedScrollToBottom = useMemo(() => debounce(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTo({
        top: chatContainerRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, 50), [chatContainerRef]);

  const scrollToBottom = useCallback(() => {
    debouncedScrollToBottom();
  }, [debouncedScrollToBottom]);

  useLayoutEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  return (
    <div
      className="chatMessages flex flex-col gap-6 p-4 sm:p-6 md:p-8 overflow-y-auto scroll-smooth bg-white flex-shrink-0 rounded-[30px] h-[60vh] max-h-[90vh] min-h-0"
      ref={chatContainerRef}
    >
      {messages.map((msg, index) => (
        <MemoizedMessage
          key={index}
          msg={msg}
          index={index}
          isLoading={isLoading}
          showFeedbackControls={
            msg.sender === 'bot' && 
            msg.text.trim() !== "" && 
            msg.text.trim() !== "Request cancelled." && 
            !msg.stopped && 
            !isLoading
          }
          feedbackType={feedbackState[index]}
          currentRatingError={ratingError[index]}
          onRate={(rating) => onRate(index, rating)}
          onPromptFeedback={() => onPromptFeedback(index)}
        />
      ))}
      

      {isLoading && messages.length > 0 &&
        (messages[messages.length - 1]?.sender === 'user' || 
         (messages[messages.length - 1]?.sender === 'bot' && messages[messages.length - 1]?.text === '')) && (
          <LoadingIndicator animatedLoadingElements={animatedLoadingElements} isLoading={isLoading} />
      )}
      

      {isLoading && messages.length === 0 && (
        <div className="flex items-center justify-center h-full">
          <div className="flex items-center space-x-2">
            <span className="text-yellow-400 animate-pulse text-xl">✨</span>
            <div className="animated-text-container flex-1">
              {animatedLoadingElements.map(item => (
                <span key={item.id} className={`animated-text ${item.animClass} text-sm font-bold`}>
                  {item.text}
                </span>
              ))}
              {isLoading && animatedLoadingElements.length === 0 && (
                <span className="animated-text in text-sm font-bold">Analyzing...</span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};


const LoadingIndicator: React.FC<{
  animatedLoadingElements: Array<{ id: string, text: string, animClass: string }>;
  isLoading: boolean;
}> = ({ animatedLoadingElements, isLoading }) => (
  <div className="self-start max-w-[90%] sm:max-w-[80%] flex flex-col">
    <div className="contents p-4 sm:p-5 md:p-6 rounded-[30px] bg-[#ececec] text-black rounded-tr-[30px] rounded-bl-[0] shadow-sm">
      <div className="flex items-center space-x-2">
        <span className="text-yellow-400 animate-pulse">✨</span>
        <div className="animated-text-container flex-1">
          {animatedLoadingElements.map(item => (
            <span key={item.id} className={`animated-text ${item.animClass} text-sm font-bold`}>
              {item.text}
            </span>
          ))}
          {isLoading && animatedLoadingElements.length === 0 && (
            <span className="animated-text in text-sm font-bold">Analyzing...</span>
          )}
        </div>
      </div>
    </div>
  </div>
);


interface MemoizedMessageProps {
  msg: Message;
  index: number;
  isLoading: boolean;
  showFeedbackControls: boolean;
  feedbackType: 'thumbs-up' | 'thumbs-down' | null;
  currentRatingError?: string;
  onRate: (rating: 'thumbs-up' | 'thumbs-down') => void;
  onPromptFeedback: () => void;
}

const MemoizedMessage = memo(
  ({ msg, index, isLoading, showFeedbackControls, feedbackType, currentRatingError, onRate, onPromptFeedback }: MemoizedMessageProps) => {
    const isUser = msg.sender === 'user';
    if (msg.sender === 'bot' && msg.text === '' && isLoading) return null;
    const markdownContent = msg.text.replace(/\\n/g, '\n').replace(/##(\d+)/g, '## $1');
    
    return (
      <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} w-full`}>
        {isUser ? (
          <div className="p-4 sm:p-5 md:p-6 rounded-[30px] max-w-[90%] sm:max-w-[80%] transition-opacity duration-300 shadow-sm bg-gradient-to-r from-[#1ea974] to-[#17a267] self-end text-white rounded-br-[0]">
            <div className="text-sm sm:text-base whitespace-pre-wrap break-words">{msg.text}</div>
          </div>
        ) : (
          <div className="self-start flex flex-col w-auto max-w-[90%] sm:max-w-[80%]">
            <div className="p-4 sm:p-5 md:p-6 rounded-[30px] transition-opacity duration-300 shadow-sm bg-[#ececec] text-black rounded-bl-[0]">
              <div className="prose prose-sm sm:prose-base max-w-none text-black break-words">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    ol: ({ children, ...props }) => {
                      const mergedChildren = React.Children.toArray(children).reduce<React.ReactNode[]>((acc, child) => {
                        if (React.isValidElement(child) && child.type === 'li') acc.push(child);
                        return acc;
                      }, []);
                      return <ol className="pl-6 sm:pl-8 list-decimal" {...props}>{mergedChildren}</ol>;
                    },
                    ul: ({ node, className, children, ...props }) => (
                      <ul className={`pl-10 sm:pl-12 list-disc ${className || ''}`} {...props}>{children}</ul>
                    ),
                    p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                    h1: ({ children }) => <h1 className="text-2xl sm:text-3xl font-bold my-3 text-black">{children}</h1>,
                    h2: ({ children }) => <h2 className="text-xl sm:text-2xl font-semibold my-3 text-black">{children}</h2>,
                    h3: ({ children }) => <h3 className="text-lg sm:text-xl font-semibold my-3 text-black">{children}</h3>,
                    h4: ({ children }) => <h4 className="text-base sm:text-lg font-semibold my-3 text-black">{children}</h4>,
                    h5: ({ children }) => <h5 className="text-sm sm:text-base font-semibold my-3 text-black">{children}</h5>,
                    h6: ({ children }) => <h6 className="text-xs sm:text-sm font-semibold my-3 text-black">{children}</h6>,
                    table: ({ children }) => (
                      <div className="overflow-x-auto w-full">
                        <table className="min-w-full border-collapse border border-gray-300 text-xs sm:text-sm">{children}</table>
                      </div>
                    ),
                    th: ({ children }) => (
                      <th className="border border-gray-300 bg-gray-100 px-2 sm:px-4 py-2 text-left font-semibold text-black whitespace-nowrap">
                        <span className="block truncate">{children}</span>
                      </th>
                    ),
                    td: ({ children }) => (
                      <td className="border border-gray-300 px-2 sm:px-4 py-2 text-black whitespace-nowrap">
                        <span className="block truncate">{children}</span>
                      </td>
                    ),
                  }}
                >{markdownContent}</ReactMarkdown>
              </div>
            </div>
            {showFeedbackControls && msg.text.trim() !== '' && 
             !msg.text.startsWith("Error:") && 
             !msg.text.startsWith("No response received") && 
             !msg.text.startsWith("Request cancelled") && (
              <div className="flex items-center justify-end mt-2 gap-x-1">
                <button 
                  onClick={onPromptFeedback} 
                  className="text-xs text-gray-600 hover:text-gray-900 hover:underline transition-colors duration-200" 
                  title="Provide detailed feedback" 
                  aria-label="Provide detailed feedback for this message"
                >
                  GIVE FEEDBACK
                </button>
                <div className="flex gap-x-1">
                  {(['thumbs-up', 'thumbs-down'] as const).map((ratingType) => (
                    <button
                      key={ratingType}
                      onClick={() => onRate(ratingType)}
                      className={`transition-all duration-200 transform hover:scale-125 rounded-full p-0 m-0 ${
                        feedbackType === ratingType ? 'opacity-100' : 'opacity-60 hover:opacity-90'
                      }`}
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
                        style={{ width: 'auto', height: 'auto' }} 
                        priority 
                        quality={100} 
                        className={`object-contain ${
                          feedbackType === ratingType && ratingType === 'thumbs-up' ? 'skgpt-tint-green-active' : ''
                        } ${
                          feedbackType === ratingType && ratingType === 'thumbs-down' ? 'skgpt-tint-red-active' : ''
                        }`} 
                      />
                    </button>
                  ))}
                </div>
              </div>
            )}
            {showFeedbackControls && currentRatingError && (
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
  (prevProps, nextProps) => (
    prevProps.msg.text === nextProps.msg.text && 
    prevProps.msg.sender === nextProps.msg.sender && 
    prevProps.index === nextProps.index && 
    prevProps.isLoading === nextProps.isLoading && 
    prevProps.showFeedbackControls === nextProps.showFeedbackControls && 
    prevProps.feedbackType === nextProps.feedbackType && 
    prevProps.currentRatingError === nextProps.currentRatingError
  )
);

MemoizedMessage.displayName = 'MemoizedMessage';

export default MessageList;
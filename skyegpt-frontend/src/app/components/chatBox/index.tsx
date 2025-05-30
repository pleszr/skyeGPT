'use client';

import React, { useState, useRef } from 'react';
import { Message } from '@/app/utils/messageManager';
import MessageList from './messageList';
import ChatInput from './chatInput';
import FeedbackModal from './feedbackModal';
import ConfirmationModal from './confirmationModal';
import { useStreamingChat } from '../../hooks/useStreamingChat';
import { useFeedbackService } from '../../hooks/useFeedbackService';

export interface ChatBoxProps {
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  className?: string;
  conversationId: string | null;
}

const ChatBox: React.FC<ChatBoxProps> = ({ messages, setMessages, className, conversationId }) => {
  const [input, setInput] = useState<string>('');
  const chatContainerRef = useRef<HTMLDivElement>(null!);
  
  const { isLoading, sendMessage, stopStreaming, dynamicLoadingTexts } = useStreamingChat(
    conversationId, 
    setMessages, 
    input, 
    setInput
  );

  const {
    feedbackState,
    ratingError,
    isFeedbackModalOpen,
    isConfirmationModalOpen,
    feedbackText,
    feedbackError,
    submitError,
    activeMessageIndex,
    modalHeader,
    textareaPlaceholder,
    confirmationMessage,
    handleRating,
    handleFeedbackPromptClick,
    handleFeedbackModalClose,
    handleFeedbackSubmit,
    handleConfirmationModalClose,
    setFeedbackText,
    setFeedbackError,
    setSubmitError
  } = useFeedbackService(conversationId);

  return (
    <div className={`flex flex-col h-full ${className || ''}`}>
      <MessageList
        messages={messages}
        isLoading={isLoading}
        dynamicLoadingTexts={dynamicLoadingTexts}
        feedbackState={feedbackState}
        ratingError={ratingError}
        onRate={handleRating}
        onPromptFeedback={handleFeedbackPromptClick}
        chatContainerRef={chatContainerRef}
      />
      
      <ChatInput
        input={input}
        setInput={setInput}
        isLoading={isLoading}
        onSend={sendMessage}
        onStop={stopStreaming}
      />

      <FeedbackModal
        isOpen={isFeedbackModalOpen && activeMessageIndex !== null}
        modalHeader={modalHeader}
        textareaPlaceholder={textareaPlaceholder}
        feedbackText={feedbackText}
        feedbackError={feedbackError}
        submitError={submitError}
        onClose={handleFeedbackModalClose}
        onSubmit={handleFeedbackSubmit}
        onFeedbackTextChange={setFeedbackText}
        onClearErrors={() => {
          setFeedbackError('');
          setSubmitError('');
        }}
      />

      <ConfirmationModal
        isOpen={isConfirmationModalOpen}
        message={confirmationMessage}
        onClose={handleConfirmationModalClose}
      />
    </div>
  );
};

export default ChatBox;
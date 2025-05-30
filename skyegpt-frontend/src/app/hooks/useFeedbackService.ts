import { useState, useCallback, useMemo, useRef } from 'react';
import { debounce } from 'lodash';
import { submitFeedbackAPI, FeedbackVotePayload } from '@/app/services/chatApiService';

export const useFeedbackService = (conversationId: string | null) => {
  const [isFeedbackModalOpen, setIsFeedbackModalOpen] = useState<boolean>(false);
  const [isConfirmationModalOpen, setIsConfirmationModalOpen] = useState<boolean>(false);
  const [feedbackText, setFeedbackText] = useState<string>('');
  const [feedbackError, setFeedbackError] = useState<string>('');
  const [submitError, setSubmitError] = useState<string>('');
  const [ratingError, setRatingError] = useState<{ [key: number]: string }>({});
  const [feedbackState, setFeedbackState] = useState<{ [key: number]: 'thumbs-up' | 'thumbs-down' | null }>({});
  const [activeMessageIndex, setActiveMessageIndex] = useState<number | null>(null);
  
  const feedbackStateRef = useRef(feedbackState);
  feedbackStateRef.current = feedbackState;

  const debouncedHandleRating = useMemo(() => debounce(async (messageIndex: number, rating: 'thumbs-up' | 'thumbs-down') => {
    const currentLocalRating = feedbackStateRef.current[messageIndex]; 
    const newLocalRating = currentLocalRating === rating ? null : rating;
    const previousLocalRatingState = feedbackStateRef.current[messageIndex];
    
    setFeedbackState((prev) => ({ ...prev, [messageIndex]: newLocalRating }));
    setRatingError((prev) => ({ ...prev, [messageIndex]: '' }));
    
    if (!conversationId) {
      setRatingError((prev) => ({ ...prev, [messageIndex]: 'Conversation ID missing. Cannot submit rating.' }));
      setFeedbackState((prev) => ({ ...prev, [messageIndex]: previousLocalRatingState })); 
      return;
    }
    
    if (newLocalRating === null) return;
    
    const vote: FeedbackVotePayload = newLocalRating === 'thumbs-up' ? 'positive' : 'negative';
    try { 
      await submitFeedbackAPI(conversationId, { vote: vote, comment: "" }); 
    } catch (error) {
      setFeedbackState((prev) => ({ ...prev, [messageIndex]: previousLocalRatingState }));
      const errorMessage = error instanceof Error && error.message.includes('Failed to connect') 
        ? 'Failed to connect to the server.' 
        : (error instanceof Error ? error.message : 'Error submitting rating.');
      setRatingError((prev) => ({ ...prev, [messageIndex]: errorMessage }));
    }
  }, 300), [conversationId]); 

  const modalHeader = useMemo(() => {
    if (activeMessageIndex === null) return 'Share Your Feedback';
    return feedbackStateRef.current[activeMessageIndex] === 'thumbs-down' ? 'Report an Issue' : 'Share Your Feedback';
  }, [activeMessageIndex]);

  const textareaPlaceholder = useMemo(() => {
    if (activeMessageIndex === null) return 'Write your feedback here...';
    return feedbackStateRef.current[activeMessageIndex] === 'thumbs-down'
      ? 'Describe the issue or why this response is problematic...'
      : 'What did you like or what could be improved?';
  }, [activeMessageIndex]);

  const confirmationMessage = useMemo(() => {
    if (activeMessageIndex === null) return 'Feedback Sent!';
    const currentRating = feedbackStateRef.current[activeMessageIndex!];
    if (currentRating === 'thumbs-down') return 'Issue Report Sent!';
    return 'Feedback Sent!';
  }, [activeMessageIndex]);

  const handleFeedbackSubmit = useCallback(async () => {
    if (activeMessageIndex === null) {
      setSubmitError('No message selected for feedback.');
      return;
    }
    if (!feedbackText.trim()) {
      setFeedbackError('Feedback cannot be empty.');
      return;
    }
    
    setFeedbackError('');
    setSubmitError('');
    
    if (!conversationId) {
      setSubmitError('conversation ID missing. Cannot submit feedback.');
      return;
    }
    
    let vote: FeedbackVotePayload = 'not_specified';
    const currentRating = feedbackStateRef.current[activeMessageIndex];
    if (currentRating === 'thumbs-up') vote = 'positive';
    else if (currentRating === 'thumbs-down') vote = 'negative';
    
    try {
      await submitFeedbackAPI(conversationId, { vote: vote, comment: feedbackText.trim() });
      setIsFeedbackModalOpen(false);
      setIsConfirmationModalOpen(true);
    } catch (error) {
      const errorMessage = error instanceof Error && error.message.includes('Failed to connect')
        ? 'Failed to connect to the server.'
        : (error instanceof Error ? error.message : 'Error submitting feedback.');
      setSubmitError(errorMessage);
    }
  }, [activeMessageIndex, feedbackText, conversationId]); 

  const handleFeedbackPromptClick = useCallback((messageIndex: number) => {
    setActiveMessageIndex(messageIndex);
    setFeedbackText('');
    setFeedbackError('');
    setSubmitError('');
    setIsFeedbackModalOpen(true);
  }, []);

  const handleFeedbackModalClose = useCallback(() => {
    setIsFeedbackModalOpen(false);
    setFeedbackError('');
    setSubmitError('');
  }, []);

  const handleConfirmationModalClose = useCallback(() => {
    setIsConfirmationModalOpen(false);
    setActiveMessageIndex(null);
    setFeedbackText('');
  }, []);

  return {
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
    handleRating: debouncedHandleRating,
    handleFeedbackPromptClick,
    handleFeedbackModalClose,
    handleFeedbackSubmit,
    handleConfirmationModalClose,
    setFeedbackText,
    setFeedbackError,
    setSubmitError
  };
};
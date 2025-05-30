'use client';

import React from 'react';

interface FeedbackModalProps {
  isOpen: boolean;
  modalHeader: string;
  textareaPlaceholder: string;
  feedbackText: string;
  feedbackError: string;
  submitError: string;
  onClose: () => void;
  onSubmit: () => void;
  onFeedbackTextChange: (value: string) => void;
  onClearErrors: () => void;
}

const FeedbackModal: React.FC<FeedbackModalProps> = ({
  isOpen,
  modalHeader,
  textareaPlaceholder,
  feedbackText,
  feedbackError,
  submitError,
  onClose,
  onSubmit,
  onFeedbackTextChange,
  onClearErrors
}) => {
  if (!isOpen) return null;

  const handleFeedbackTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onFeedbackTextChange(e.target.value);
    if (feedbackError || submitError) {
      onClearErrors();
    }
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-transparent backdrop-blur-md z-50 p-4">
      <div 
        className="bg-white rounded-[20px] shadow-xl p-6 w-full max-w-lg flex flex-col gap-4" 
        role="dialog" 
        aria-labelledby="feedback-modal-header" 
        aria-modal="true"
      >
        <div className="flex justify-between items-center">
          <h2 
            id="feedback-modal-header" 
            className="text-lg font-semibold text-gray-800 flex-1 text-center"
          >
            {modalHeader}
          </h2>
          <button 
            onClick={onClose} 
            className="text-gray-500 hover:text-gray-700 text-2xl leading-none" 
            aria-label="Close feedback modal"
          >
            ×
          </button>
        </div>
        <div className="flex flex-col gap-2 flex-1">
          <textarea
            className={`w-full min-h-[100px] p-3 rounded-[10px] bg-gray-100 text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#1ea974] resize-none border ${
              feedbackError || submitError ? 'border-red-500 ring-red-500' : 'border-gray-300'
            }`}
            placeholder={textareaPlaceholder}
            value={feedbackText}
            onChange={handleFeedbackTextChange}
            aria-invalid={!!feedbackError || !!submitError}
            aria-describedby={
              feedbackError ? 'feedback-input-error' : 
              submitError ? 'feedback-submit-error' : 
              undefined
            }
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
            onClick={onSubmit}
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
  );
};

export default FeedbackModal;
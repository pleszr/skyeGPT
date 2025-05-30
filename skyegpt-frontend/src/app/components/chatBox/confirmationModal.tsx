'use client';

import React from 'react';

interface ConfirmationModalProps {
  isOpen: boolean;
  message: string;
  onClose: () => void;
}

const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  isOpen,
  message,
  onClose
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-transparent backdrop-blur-md z-50 p-4">
      <div 
        className="bg-white rounded-[20px] shadow-xl p-6 w-full max-w-md flex flex-col gap-4 items-center" 
        role="alertdialog" 
        aria-labelledby="confirmation-modal-header" 
        aria-describedby="confirmation-modal-description" 
        aria-modal="true"
      >
        <div className="w-full flex justify-between items-center">
          <span className="w-6"></span>
          <h2 
            id="confirmation-modal-header" 
            className="text-lg font-semibold text-gray-800 text-center flex-1"
          >
            {message}
          </h2>
          <button 
            onClick={onClose} 
            className="text-gray-500 hover:text-gray-700 text-2xl leading-none" 
            aria-label="Close confirmation"
          >
            ×
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
        <p 
          id="confirmation-modal-description" 
          className="text-center text-gray-600"
        >
          Thank you for your input!
        </p>
      </div>
    </div>
  );
};

export default ConfirmationModal;
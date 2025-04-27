'use client';

import Image from 'next/image';
import React, { useState, useEffect } from 'react';
import ChatBox from '@/app/components/ChatBox';
import { Message } from '@/app/utils/MessageManager';

const HomePage = () => {
  const [chromaMessages, setChromaMessages] = useState<Message[]>([]);
  const backendHost = process.env.NEXT_PUBLIC_SKYEGPT_BACKEND_HOST || 'http://localhost:8000';

  const createThread = async () => {
    try {
      const response = await fetch(`${backendHost}/createThread`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        alert(`Could not create new thread: ${JSON.stringify(response)}`);
      }

      const data = await response.json();
      console.log('Thread created', data.thread_id);
      localStorage.setItem('threadId', data.thread_id);

      console.log('Chroma conversation created', data.chroma_conversation_id);
      localStorage.setItem('chroma_conversation_id', data.chroma_conversation_id);
    } catch (error) {
      console.error('Error creating thread:', error);
    }
  };

  useEffect(() => {
    createThread();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const askEndpointChroma = `${backendHost}/askChroma`;

  return (
    <div className="w-screen h-screen max-w-full max-h-full flex flex-col">
      <header className="flex justify-between items-center h-[80px] sm:h-[100px] px-4 sm:px-8 md:px-12 py-4 sm:py-6">
        <Image src="/logo.svg" alt="logo" width={120} height={60} className="h-[60px] sm:h-[80px]" />
        <span className="text-xs sm:text-sm text-gray-600">
          design by Fanni Wihl | frontend by Marcell Monoki & Csaba Sallai
        </span>
      </header>
      <div className="flex-1">
        <div className="flex flex-col pt-4 sm:pt-6 pb-8 sm:pb-12 h-full mx-auto w-full max-w-[90%] sm:max-w-[1230px]">
          <div className="flex h-full flex-col">
            <div className="flex h-[40px] sm:h-[50px] gap-2 sm:gap-3">
              <div className="flex justify-center items-center text-base sm:text-xl bg-white min-w-[160px] sm:min-w-[180px] h-full rounded-t-[20px] shadow-md cursor-pointer hover:bg-gray-50 transition-colors duration-200 p-2 sm:p-3">
                Ask Skye Documentation
              </div>
            </div>
            <div className="flex-1 bg-white shadow-lg rounded-[0_40px_40px_40px] p-4 sm:p-6 md:p-8">
              <div className="h-full">
                <ChatBox
                  title="Ask GPT Chroma"
                  askEndpoint={askEndpointChroma}
                  messages={chromaMessages}
                  setMessages={setChromaMessages}
                  className="gptChroma"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
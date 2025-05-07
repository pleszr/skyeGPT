'use client';

import Image from 'next/image';
import React, { useState, useEffect } from 'react';
import ChatBox from '@/app/components/chatBox';
import { Message } from '@/app/utils/messageManager';

const HomePage = () => {
  const [chromaMessages, setChromaMessages] = useState<Message[]>([]);
  const backendHost = process.env.NEXT_PUBLIC_SKYEGPT_BACKEND_HOST || 'http://localhost:8000';

  const createConversation = async () => {
    try {
      const response = await fetch(`${backendHost}/ask/conversation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Could not create new conversation: ${response.status}`);
      }

      const data = await response.json();
      console.log('Conversation created', data.conversation_id);
      localStorage.setItem('chroma_conversation_id', data.conversation_id);

    } catch (error) {
      console.error('Error creating conversation:', error);
      alert('Failed to create conversation. Please try again.');
    }
  };

  useEffect(() => {
    createConversation();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const askEndpointChroma = `${backendHost}/ask/response/stream`;

  return (
    <div className="w-screen min-h-screen max-w-full flex flex-col overflow-hidden">
      <div className="flex-1 flex flex-col md:flex-row mx-auto w-full max-w-[1530px] px-4 sm:px-8 md:px-12">
        <div className="hidden md:flex flex-col items-center justify-center w-[200px] md:w-[300px] py-4 relative shrink-0">
          <Image
            src="/logo.png"
            alt="SkyeGPT logo"
            width={191}
            height={149}
            style={{ height: 'auto', width: 'auto' }}
            className="w-[150px] md:w-[191px] h-auto mb-4"
          />
          <Image
            src="/gears.png"
            alt="Gears"
            width={267}
            height={380}
            className="w-[150px] md:w-[200px] h-auto mb-4"
            style={{ color: 'transparent' }}
          />
          <Image
            src="/robot.png"
            alt="Robot"
            width={300}
            height={300}
            priority
            className="w-[150px] md:w-[300px] h-auto relative -mr-8 md:-mr-16"
          />
        </div>

        <div className="flex md:hidden justify-center py-8">
          <Image
            src="/logo.png"
            alt="SkyeGPT logo"
            width={191}
            height={149}
            style={{ height: 'auto', width: 'auto' }}
            className="w-[150px] h-auto max-w-[90%] max-h-[150px]"
          />
        </div>

        <div className="flex-1 flex flex-col min-h-0">
          <div className="flex flex-col pt-2 sm:pt-4 pb-4 sm:pb-6 w-full h-full">
            <div className="flex flex-col h-full">
              <div className="flex h-[40px] sm:h-[50px] gap-2 sm:gap-3"></div>
              <div className="flex-1 bg-white shadow-lg rounded-[40px] p-4 sm:p-6 md:p-8 min-h-0">
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
          <footer className="text-center text-xs sm:text-sm text-gray-600 mt-4 shrink-0 translate-y-[-20px]">
            SkyeGPT can make mistakes. If you find the answer strange, verify the results and give feedback!
          </footer>
        </div>
      </div>
    </div>
  );
};

export default HomePage;